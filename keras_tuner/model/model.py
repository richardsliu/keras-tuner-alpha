import keras
import jax
import jax.numpy as jnp
import numpy as np
import functools
from typing import Optional, Any
from abc import ABC, abstractmethod
from keras_nlp.models import CausalLM
from keras.src.backend.common import global_state
from keras.distribution import set_distribution
from keras_tuner.model.sharding import ShardingStrategy
from keras_tuner.model.sharding.utils import (
    print_elements_that_are_unsharded_and_large_in_pytree,
)
from keras_tuner.model.checkpoint_loader.maxtext.from_huggingface import (
    load_hf_weights_into_maxtext_model,
)
from keras_tuner.model.checkpoint_loader.maxtext.utils import (
    get_maxtext_model_type_from_hf_handle,
)


class ModelValidationMixin:
    """Mixin providing common model validation functionality."""

    def validate_model(self, model: Any) -> None:
        """Validates the model by ensuring it is not None and checking sharding status."""
        if model is None:
            raise ValueError("Model has not been successfully created.")
        print_elements_that_are_unsharded_and_large_in_pytree(model)


class Model(ABC, ModelValidationMixin):
    """
    Base class for a Kithara model. Provides common attributes and methods for model management.

    Attributes:
        precision (Optional[str]): Precision of activations, e.g., 'float32', 'mixed_float16'.
        model (keras.Model): The Keras model instance.
    """

    def __init__(
        self,
        model: keras.Model,
        sharding_strategy: ShardingStrategy = None,
        precision: Optional[str] = None,
    ):
        self._precision = precision
        self._sharding_strategy = sharding_strategy
        self._model = model
        self.validate_model(model)

    @property
    def model(self) -> keras.Model:
        return self._model

    @property
    def precision(self) -> Optional[str]:
        return self._precision

    @property
    def sharding_strategy(self) -> Optional[ShardingStrategy]:
        return self._sharding_strategy

    @classmethod
    @abstractmethod
    def from_preset(
        cls,
        preset_handle: str,
        sharding_strategy: Optional[ShardingStrategy] = None,
        precision: Optional[str] = None,
        **kwargs,
    ) -> "Model":
        """Load a model from a preset (local or cloud)."""
        pass

    def __getattr__(self, name: str) -> Any:
        """Delegates unknown attributes or methods to the underlying Keras model."""
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass

        # Delegate to the model if the attribute is not found
        model = getattr(self, "model", None)
        if model is None:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

        try:
            return getattr(model, name)
        except AttributeError as e:
            raise AttributeError(
                f"'{self.__class__.__name__}' object and its model have no attribute '{name}'"
            ) from e


class KerasModel(Model):
    """
    A Kithara model wrapper for KerasHub models, providing a Keras-compatible interface.

    Attributes:
        model_handle (str): Model identifier, e.g., "hf://google/gemma-2-2b".
        lora_rank (Optional[int]): Rank for LoRA adaptation (disabled if None).
    """

    @classmethod
    def from_preset(
        cls,
        model_handle: str,
        lora_rank: Optional[int] = None,
        precision: Optional[str] = None,
        sharding_strategy: Optional[ShardingStrategy] = None,
        **kwargs,
    ) -> "KerasModel":
        """Load a Keras model from a preset and apply LoRA if specified."""
        set_precision(precision)
        set_global_sharding_strategy(sharding_strategy)

        model = CausalLM.from_preset(model_handle, preprocessor=None, **kwargs)
        if lora_rank:
            model.backbone.enable_lora(rank=lora_rank)

        return cls(model, sharding_strategy, precision)


class MaxTextModel(Model):
    """
    A Kithara wrapper for MaxText models, providing a Keras-compatible interface.

    Attributes:
        model_name (str): MaxText model name.
        seq_len (int): Maximum sequence length.
        global_batch_size (int): Batch size across all devices.
    """

    @classmethod
    def from_random(
        cls,
        precision: Optional[str] = None,
        model_name: Optional[str] = None,
        seq_len: Optional[int] = None,
        per_device_batch_size: Optional[int] = None,
    ) -> "MaxTextModel":
        """Create a randomly initialized MaxText model with the given configuration."""
        set_precision(precision)
        sharding_strategy, model = cls._initialize_random_model(
            model_name, seq_len, per_device_batch_size
        )
        return cls(model, sharding_strategy, precision)

    @classmethod
    def from_preset(
        cls,
        preset_handle: str,
        seq_len: int,
        per_device_batch_size: int,
        precision: Optional[str],
        **kwargs,
    ) -> "MaxTextModel":
        """Create a MaxText model initialized with weights from HuggingFace Hub."""
        set_precision(precision)
        model_name = get_maxtext_model_type_from_hf_handle(preset_handle)
        sharding_strategy, model = cls._initialize_random_model(
            model_name, seq_len, per_device_batch_size
        )
        model = load_hf_weights_into_maxtext_model(preset_handle, model)

        return cls(model, sharding_strategy, precision)

    @staticmethod
    def _initialize_random_model(
        model_name: str,
        seq_len: int,
        per_device_batch_size: int,
    ) -> tuple[ShardingStrategy, keras.Model]:
        """Initialize a random MaxText model with sharding configuration."""
        from keras_tuner.model.converter.maxtext import (
            convert_maxtext_model_to_keras_model,
            get_maxtext_config,
        )
        from keras_tuner.model.sharding.maxtext import MaxTextSharding
        from maxtext.MaxText.train import setup_mesh_and_model
        from maxtext.MaxText.max_utils import (
            get_abstract_state,
            unbox_logicallypartioned,
        )

        maxtext_config = get_maxtext_config(model_name)
        global_batch_size = per_device_batch_size * jax.device_count()

        # Initialize the model and mesh configuration
        init_rng, _, _, jax_mesh, model, _, tx = setup_mesh_and_model(maxtext_config)

        # Initialize model parameters
        def init_initial_state(model, rng):
            input_shape = (global_batch_size, seq_len)
            return model.init(
                {"params": rng, "dropout": rng, "aqt": rng},
                np.ones(input_shape, dtype=jnp.int32),
                np.ones(input_shape, dtype=jnp.int32),
            )

        init_state_partial = functools.partial(init_initial_state, model)

        # Get the model state and shardings
        _, _, state_shardings = get_abstract_state(
            model, tx, maxtext_config, init_rng, jax_mesh, is_training=True
        )
        state = jax.jit(
            init_state_partial, in_shardings=None, out_shardings=state_shardings.params
        )(init_rng)
        state = unbox_logicallypartioned(state)

        # Set sharding strategy
        sharding_strategy = MaxTextSharding(jax_mesh, state_shardings)
        set_global_sharding_strategy(sharding_strategy)

        # Convert to Keras model format
        model = convert_maxtext_model_to_keras_model(
            model, state, seq_len, global_batch_size
        )
        return sharding_strategy, model


def set_precision(precision: Optional[str]) -> None:
    """Set global mixed-precision policy for model weights and activations."""
    if precision:
        policy = global_state.get_global_attribute("dtype_policy", None)
        if policy:
            print(f"Overriding existing policy: {policy}")
        keras.mixed_precision.set_global_policy(precision)


def set_global_sharding_strategy(strategy: Optional[ShardingStrategy]) -> None:
    """Set the global sharding strategy for model and data distribution."""
    if strategy:
        if global_state.get_global_attribute("distribution") is not None:
            print("WARNING: Distribution strategy is being overridden.")
        set_distribution(strategy.distribution)
        global_state.set_global_attribute("DATA_SHARDING", strategy.data_sharding)
