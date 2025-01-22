import numpy as np
from kithara.model import supported_models


def GEMMA2_MAXTEXT_TO_HF_PARAM_MAPPING(config, scan_layers=False):
    """Returns mapping between MaxText and HuggingFace Gemma2 weight paths.

    Args:
        config (dict): Model configuration dictionary containing at least 'num_hidden_layers'.
        scan_layers (bool, optional): Whether the MaxText model uses layer scanning optimization.
            When True, decoder layers are stacked into a single tensor [dim1, #layers, dim2].
            Defaults to False.

    Returns:
        dict: A mapping where:
            - Keys are MaxText parameter paths
            - Values are either:
                - Single strings (HF parameter path) for unscanned parameters
                - Lists of strings (HF parameter paths) for stacked layers when scan_layers=True

    Notes:
        - MaxText uses a paired layer approach where two HF decoder layers are treated as
            one MaxText decoder layer.
        - MaxText layer i corresponds to HF layers 2i and 2i+1
        - Local components map to even-numbered HF decoder layers (0, 2, 4...)
        - Global components map to odd-numbered HF decoder layers (1, 3, 5...)
    """

    nlayers = config["num_hidden_layers"]
    mapping = {
        "params-token_embedder-embedding": "model.embed_tokens.weight",
        "params-decoder-decoder_norm-scale": "model.norm.weight",
    }
    if scan_layers:
        mapping = {
            **mapping,
            "params-decoder-layers-pre_self_attention_norm_global-scale": [
                f"model.layers.{i}.input_layernorm.weight" for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-mlp_global-wo-kernel": [
                f"model.layers.{i}.mlp.down_proj.weight" for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-mlp_global-wi_1-kernel": [
                f"model.layers.{i}.mlp.up_proj.weight" for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-mlp_global-wi_0-kernel": [
                f"model.layers.{i}.mlp.gate_proj.weight" for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-post_self_attention_norm_global-scale": [
                f"model.layers.{i}.post_attention_layernorm.weight"
                for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-post_ffw_norm_global-scale": [
                f"model.layers.{i}.post_feedforward_layernorm.weight"
                for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-pre_ffw_norm_global-scale": [
                f"model.layers.{i}.pre_feedforward_layernorm.weight"
                for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-self_attention_global-key-kernel": [
                f"model.layers.{i}.self_attn.k_proj.weight"
                for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-self_attention_global-out-kernel": [
                f"model.layers.{i}.self_attn.o_proj.weight"
                for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-self_attention_global-query-kernel": [
                f"model.layers.{i}.self_attn.q_proj.weight"
                for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-self_attention_global-value-kernel": [
                f"model.layers.{i}.self_attn.v_proj.weight"
                for i in range(1, nlayers, 2)
            ],
            "params-decoder-layers-pre_self_attention_norm_local-scale": [
                f"model.layers.{i}.input_layernorm.weight" for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-mlp_local-wo-kernel": [
                f"model.layers.{i}.mlp.down_proj.weight" for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-mlp_local-wi_1-kernel": [
                f"model.layers.{i}.mlp.up_proj.weight" for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-mlp_local-wi_0-kernel": [
                f"model.layers.{i}.mlp.gate_proj.weight" for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-post_self_attention_norm_local-scale": [
                f"model.layers.{i}.post_attention_layernorm.weight"
                for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-post_ffw_norm_local-scale": [
                f"model.layers.{i}.post_feedforward_layernorm.weight"
                for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-pre_ffw_norm_local-scale": [
                f"model.layers.{i}.pre_feedforward_layernorm.weight"
                for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-self_attention_local-key-kernel": [
                f"model.layers.{i}.self_attn.k_proj.weight"
                for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-self_attention_local-out-kernel": [
                f"model.layers.{i}.self_attn.o_proj.weight"
                for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-self_attention_local-query-kernel": [
                f"model.layers.{i}.self_attn.q_proj.weight"
                for i in range(0, nlayers, 2)
            ],
            "params-decoder-layers-self_attention_local-value-kernel": [
                f"model.layers.{i}.self_attn.v_proj.weight"
                for i in range(0, nlayers, 2)
            ],
        }
    # Case 2: scan_layer=False
    else:
        for maxtext_layer_idx in range(0, nlayers // 2):
            local_layer_idx = maxtext_layer_idx * 2
            global_layer_idx = maxtext_layer_idx * 2 + 1
            layer_mapping = {
                f"params-decoder-layers_{maxtext_layer_idx}-pre_self_attention_norm_global-scale": f"model.layers.{global_layer_idx}.input_layernorm.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_global-wo-kernel": f"model.layers.{global_layer_idx}.mlp.down_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_global-wi_1-kernel": f"model.layers.{global_layer_idx}.mlp.up_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_global-wi_0-kernel": f"model.layers.{global_layer_idx}.mlp.gate_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-post_self_attention_norm_global-scale": f"model.layers.{global_layer_idx}.post_attention_layernorm.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-post_ffw_norm_global-scale": f"model.layers.{global_layer_idx}.post_feedforward_layernorm.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-pre_ffw_norm_global-scale": f"model.layers.{global_layer_idx}.pre_feedforward_layernorm.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_global-key-kernel": f"model.layers.{global_layer_idx}.self_attn.k_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_global-out-kernel": f"model.layers.{global_layer_idx}.self_attn.o_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_global-query-kernel": f"model.layers.{global_layer_idx}.self_attn.q_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_global-value-kernel": f"model.layers.{global_layer_idx}.self_attn.v_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-pre_self_attention_norm_local-scale": f"model.layers.{local_layer_idx}.input_layernorm.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_local-wo-kernel": f"model.layers.{local_layer_idx}.mlp.down_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_local-wi_1-kernel": f"model.layers.{local_layer_idx}.mlp.up_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_local-wi_0-kernel": f"model.layers.{local_layer_idx}.mlp.gate_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-post_self_attention_norm_local-scale": f"model.layers.{local_layer_idx}.post_attention_layernorm.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-post_ffw_norm_local-scale": f"model.layers.{local_layer_idx}.post_feedforward_layernorm.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-pre_ffw_norm_local-scale": f"model.layers.{local_layer_idx}.pre_feedforward_layernorm.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_local-key-kernel": f"model.layers.{local_layer_idx}.self_attn.k_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_local-out-kernel": f"model.layers.{local_layer_idx}.self_attn.o_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_local-query-kernel": f"model.layers.{local_layer_idx}.self_attn.q_proj.weight",
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_local-value-kernel": f"model.layers.{local_layer_idx}.self_attn.v_proj.weight",
            }
            mapping = {**mapping, **layer_mapping}
    return mapping


def GEMMA2_MAXTEXT_TO_HF_PARAM_HOOK_FN(config, scan_layers=False, saving_to_hf=False):
    """Creates parameter transformation functions for converting between MaxText and
    HuggingFace formats.

    This function generates a mapping of transformation functions that handle the necessary
    conversions between MaxText and HuggingFace parameter formats, including operations like
    padding, reshaping, and scaling.

    Args:
        config (dict): Model configuration dictionary that must contain:
            - num_hidden_layers (int): Number of layers in the model
            - head_dim (int): Dimension of attention heads
            - hidden_size (int): Model's hidden dimension size

        scan_layers (bool, optional): Controls the output format for layer parameters:
            - True: Returns transformation functions for batched layer parameters
            - False: Returns transformation functions for individual layer parameters
            Defaults to False.

        saving_to_hf (bool, optional): Determines the direction of transformation:
            - True: MaxText → HuggingFace conversion
            - False: HuggingFace → MaxText conversion
            Defaults to False.

    Returns:
        dict: Parameter transformation mapping where:
            - Keys: MaxText parameter names (str)
            - Values: Either:
                - callable: Single transformation function
                - list[callable]: List of transformation functions to be applied in sequence

    Transformation Details:
        The function handles several types of parameter transformations:
        1. Embedding layer padding:
            - HF shape: [256000, d_model]
            - MaxText shape: [256128, d_model] (padded for performance)
        2. Layer normalization scaling:
            - Adds/subtracts 1.0 depending on direction
        3. Attention query scaling:
            - Scales by sqrt(head_dim) or its inverse

        4. Kernel reshaping:
            - Handles dimension transposition and reshaping between formats
    """
    nlayers = config["num_hidden_layers"]

    def pad_hf_embedding_layer(input_tensor, target_shape):
        """
        Note:
            HF embedding weights shape =  [256000,d_model]
            MaxText embedding weights shape = [256128,d_model]
            MaxText pad Gemma2 embedding to 256128 for better performance.
        """
        # TODO(wenxindongwork), Perhaps, this dtype should be the activation dtype
        normalizer = np.dtype("float32").type(config["hidden_size"] ** 0.5)

        def to_hf():
            target_tensor = input_tensor[: target_shape[0], : target_shape[1]]
            target_tensor = target_tensor / normalizer
            target_tensor = target_tensor.astype(input_tensor.dtype)
            return target_tensor

        def from_hf():
            target_tensor = np.zeros(target_shape, dtype=input_tensor.dtype)
            target_tensor[: input_tensor.shape[0], : input_tensor.shape[1]] = (
                input_tensor
            )
            target_tensor = target_tensor * normalizer
            target_tensor = target_tensor.astype(input_tensor.dtype)
            return target_tensor

        if saving_to_hf:
            return to_hf()
        else:
            return from_hf()

    def reshape_kernel(input_tensor, target_shape):
        def to_hf():
            flipped_target_shape = np.flip(np.array(target_shape))
            return input_tensor.reshape(flipped_target_shape).transpose()

        def from_hf():
            return input_tensor.transpose().reshape(target_shape)

        if saving_to_hf:
            return to_hf()
        else:
            return from_hf()

    def scale_rmsnorm_layer(input_tensor, target_shape):
        def to_hf():
            return (input_tensor - 1.0).reshape(target_shape)

        def from_hf():
            return (input_tensor + 1.0).reshape(target_shape)

        if saving_to_hf:
            return to_hf()
        else:
            return from_hf()

    def scale_query_layer(input_tensor, target_shape):
        def to_hf():
            depth_scale = np.dtype("float32").type(np.sqrt(config["head_dim"]))
            return (input_tensor * depth_scale).astype(input_tensor.dtype)

        def from_hf():
            depth_scale = np.dtype("float32").type(1 / np.sqrt(config["head_dim"]))
            return (input_tensor * depth_scale).astype(input_tensor.dtype)

        if saving_to_hf:
            return to_hf()
        else:
            return from_hf()

    mapping = {
        "params-token_embedder-embedding": pad_hf_embedding_layer,
        "params-decoder-decoder_norm-scale": scale_rmsnorm_layer,
    }
    if scan_layers:
        mapping = {
            **mapping,
            f"params-decoder-layers-self_attention_global-query-kernel": [
                reshape_kernel,
                scale_query_layer,
            ],
            f"params-decoder-layers-self_attention_local-query-kernel": [
                reshape_kernel,
                scale_query_layer,
            ],
            f"params-decoder-layers-self_attention_global-key-kernel": reshape_kernel,
            f"params-decoder-layers-self_attention_local-key-kernel": reshape_kernel,
            f"params-decoder-layers-self_attention_global-value-kernel": reshape_kernel,
            f"params-decoder-layers-self_attention_local-value-kernel": reshape_kernel,
            f"params-decoder-layers-mlp_global-wo-kernel": reshape_kernel,
            f"params-decoder-layers-mlp_global-wi_1-kernel": reshape_kernel,
            f"params-decoder-layers-mlp_global-wi_0-kernel": reshape_kernel,
            f"params-decoder-layers-self_attention_global-out-kernel": reshape_kernel,
            f"params-decoder-layers-mlp_local-wo-kernel": reshape_kernel,
            f"params-decoder-layers-mlp_local-wi_1-kernel": reshape_kernel,
            f"params-decoder-layers-mlp_local-wi_0-kernel": reshape_kernel,
            f"params-decoder-layers-self_attention_local-out-kernel": reshape_kernel,
            f"params-decoder-layers-pre_self_attention_norm_global-scale": scale_rmsnorm_layer,
            f"params-decoder-layers-post_self_attention_norm_global-scale": scale_rmsnorm_layer,
            f"params-decoder-layers-post_ffw_norm_global-scale": scale_rmsnorm_layer,
            f"params-decoder-layers-pre_ffw_norm_global-scale": scale_rmsnorm_layer,
            f"params-decoder-layers-pre_self_attention_norm_local-scale": scale_rmsnorm_layer,
            f"params-decoder-layers-post_self_attention_norm_local-scale": scale_rmsnorm_layer,
            f"params-decoder-layers-post_ffw_norm_local-scale": scale_rmsnorm_layer,
            f"params-decoder-layers-pre_ffw_norm_local-scale": scale_rmsnorm_layer,
        }
    else:
        for maxtext_layer_idx in range(nlayers // 2):
            mapping = {
                **mapping,
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_global-query-kernel": [
                    reshape_kernel,
                    scale_query_layer,
                ],
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_local-query-kernel": [
                    reshape_kernel,
                    scale_query_layer,
                ],
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_global-key-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_local-key-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_global-value-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_local-value-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_global-wo-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_global-wi_1-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_global-wi_0-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_global-out-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_local-wo-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_local-wi_1-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-mlp_local-wi_0-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-self_attention_local-out-kernel": reshape_kernel,
                f"params-decoder-layers_{maxtext_layer_idx}-pre_self_attention_norm_global-scale": scale_rmsnorm_layer,
                f"params-decoder-layers_{maxtext_layer_idx}-post_self_attention_norm_global-scale": scale_rmsnorm_layer,
                f"params-decoder-layers_{maxtext_layer_idx}-post_ffw_norm_global-scale": scale_rmsnorm_layer,
                f"params-decoder-layers_{maxtext_layer_idx}-pre_ffw_norm_global-scale": scale_rmsnorm_layer,
                f"params-decoder-layers_{maxtext_layer_idx}-pre_self_attention_norm_local-scale": scale_rmsnorm_layer,
                f"params-decoder-layers_{maxtext_layer_idx}-post_self_attention_norm_local-scale": scale_rmsnorm_layer,
                f"params-decoder-layers_{maxtext_layer_idx}-post_ffw_norm_local-scale": scale_rmsnorm_layer,
                f"params-decoder-layers_{maxtext_layer_idx}-pre_ffw_norm_local-scale": scale_rmsnorm_layer,
            }
    return mapping


# LLama3.1

def LLAMA31_MAXTEXT_TO_HF_PARAM_MAPPING(config, scan_layers=False):
    """
    Returns a dictionary mapping from MaxText parameter names to
    HuggingFace LLaMA3.1 parameter names.

    Args:
        config (dict): Model configuration dictionary containing:
            - num_hidden_layers (int): The number of decoder layers.
        scan_layers (bool, optional): If True, MaxText layers are 'stacked'
            into a single param. Defaults to False.

    Returns:
        dict: A mapping from MaxText parameter names to HF parameter names (str)
              or lists of names (if scan_layers=True).
    """
    n_layers = config["num_hidden_layers"]

    mapping = {
        "max_text_layer/params-token_embedder-embedding": "model.embed_tokens.weight",
        "max_text_layer/params-decoder-logits_dense-kernel": "lm_head.weight",
        "max_text_layer/params-decoder-decoder_norm-scale": "model.norm.weight",
    }

    if scan_layers:
        mapping[
            "max_text_layer/params-decoder-layers-self_attention-query-kernel"
        ] = [
            f"model.layers.{layer_idx}.self_attn.q_proj.weight"
            for layer_idx in range(n_layers)
        ]
        mapping[
            "max_text_layer/params-decoder-layers-self_attention-key-kernel"
        ] = [
            f"model.layers.{layer_idx}.self_attn.k_proj.weight"
            for layer_idx in range(n_layers)
        ]
        mapping[
            "max_text_layer/params-decoder-layers-self_attention-value-kernel"
        ] = [
            f"model.layers.{layer_idx}.self_attn.v_proj.weight"
            for layer_idx in range(n_layers)
        ]
        mapping[
            "max_text_layer/params-decoder-layers-self_attention-out-kernel"
        ] = [
            f"model.layers.{layer_idx}.self_attn.o_proj.weight"
            for layer_idx in range(n_layers)
        ]
        mapping[
            "max_text_layer/params-decoder-layers-mlp-wi_0-kernel"
        ] = [
            f"model.layers.{layer_idx}.mlp.gate_proj.weight"
            for layer_idx in range(n_layers)
        ]
        mapping[
            "max_text_layer/params-decoder-layers-mlp-wi_1-kernel"
        ] = [
            f"model.layers.{layer_idx}.mlp.up_proj.weight"
            for layer_idx in range(n_layers)
        ]
        mapping[
            "max_text_layer/params-decoder-layers-mlp-wo-kernel"
        ] = [
            f"model.layers.{layer_idx}.mlp.down_proj.weight"
            for layer_idx in range(n_layers)
        ]
        mapping[
            "max_text_layer/params-decoder-layers-pre_self_attention_layer_norm-scale"
        ] = [
            f"model.layers.{layer_idx}.input_layernorm.weight"
            for layer_idx in range(n_layers)
        ]
        mapping[
            "max_text_layer/params-decoder-layers-post_self_attention_layer_norm-scale"
        ] = [
            f"model.layers.{layer_idx}.post_attention_layernorm.weight"
            for layer_idx in range(n_layers)
        ]
    else:
        for layer_idx in range(n_layers):
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-self_attention-query-kernel"
            ] = f"model.layers.{layer_idx}.self_attn.q_proj.weight"
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-self_attention-key-kernel"
            ] = f"model.layers.{layer_idx}.self_attn.k_proj.weight"
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-self_attention-value-kernel"
            ] = f"model.layers.{layer_idx}.self_attn.v_proj.weight"
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-self_attention-out-kernel"
            ] = f"model.layers.{layer_idx}.self_attn.o_proj.weight"
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-mlp-wi_0-kernel"
            ] = f"model.layers.{layer_idx}.mlp.gate_proj.weight"
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-mlp-wi_1-kernel"
            ] = f"model.layers.{layer_idx}.mlp.up_proj.weight"
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-mlp-wo-kernel"
            ] = f"model.layers.{layer_idx}.mlp.down_proj.weight"
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-pre_self_attention_layer_norm-scale"
            ] = f"model.layers.{layer_idx}.input_layernorm.weight"
            mapping[
                f"max_text_layer/params-decoder-layers_{layer_idx}-post_self_attention_layer_norm-scale"
            ] = f"model.layers.{layer_idx}.post_attention_layernorm.weight"

    return mapping

def LLAMA31_MAXTEXT_TO_HF_PARAM_HOOK_FN(config, scan_layers=False, saving_to_hf=False):
    """Creates parameter transformation functions for converting between MaxText and
    HuggingFace formats.

    This function generates a mapping of transformation functions that handle the necessary
    conversions between MaxText and HuggingFace parameter formats, including operations like
    reshaping.

    Args:
        config (dict): Model configuration dictionary that must contain:
            - num_hidden_layers (int): Number of layers in the model
            - head_dim (int): Dimension of attention heads
            - hidden_size (int): Model's hidden dimension size

        scan_layers (bool, optional): Controls the output format for layer parameters:
            - True: Returns transformation functions for batched layer parameters
            - False: Returns transformation functions for individual layer parameters
            Defaults to False.

        saving_to_hf (bool, optional): Determines the direction of transformation:
            - True: MaxText → HuggingFace conversion
            - False: HuggingFace → MaxText conversion
            Defaults to False.

    Returns:
        dict: Parameter transformation mapping where:
            - Keys: MaxText parameter names (str)
            - Values: Either:
                - callable: Single transformation function
                - list[callable]: List of transformation functions to be applied in sequence

    Transformation Details:
        The function handles reshaping and Transpose 2d:
        1. Kernel reshaping:
            - Handles dimension transposition and reshaping between formats
        2. Transpose 2D
            - Transposes 2d matrix
    """
    nlayers = config["num_hidden_layers"]

    def reshape_kernel(input_tensor, target_shape):
        def to_hf():
            flipped_target_shape = np.flip(np.array(target_shape))
            return input_tensor.reshape(flipped_target_shape).transpose()

        def from_hf():
            return input_tensor.transpose().reshape(target_shape)

        if saving_to_hf:
            return to_hf()
        else:
            return from_hf()

    hook_fns = {}
    def identity_transform(input_array, target_shape):
        return input_array  
    
    def transpose_transform(input_array, target_shape):
        def transpose_2d(input_array):
            return input_array.transpose()
        return transpose_2d(input_array)

    hook_fns["max_text_layer/params-token_embedder-embedding"] = identity_transform
    hook_fns["max_text_layer/params-decoder-logits_dense-kernel"] = transpose_transform
    if scan_layers:
        hook_fns = {
            **hook_fns,
            f"max_text_layer/params-decoder-layers-self_attention-query-kernel": reshape_kernel,
            f"max_text_layer/params-decoder-layers-self_attention-key-kernel": reshape_kernel,
            f"max_text_layer/params-decoder-layers-self_attention-value-kernel": reshape_kernel,
            f"max_text_layer/params-decoder-layers-self_attention-out-kernel": reshape_kernel,
            f"max_text_layer/params-decoder-layers-mlp-wi_0-kernel": reshape_kernel,
            f"max_text_layer/params-decoder-layers-mlp-wi_1-kernel": reshape_kernel,
            f"pre_self_attention_layer_norm-scale": reshape_kernel,
            f"post_self_attention_layer_norm-scale": reshape_kernel,
            f"max_text_layer/params-decoder-layers-pre_self_attention_layer_norm-scale": reshape_kernel,
            f"max_text_layer/params-decoder-layers-mlp-wo-kernel": reshape_kernel,
        }
    else:
        for layer_idx in range(nlayers):
            maxtext_name = f"max_text_layer/params-decoder-layers_{layer_idx}-self_attention-query-kernel"
            hook_fns[maxtext_name] = reshape_kernel 
            maxtext_name = f"max_text_layer/params-decoder-layers_{layer_idx}-self_attention-key-kernel"
            hook_fns[maxtext_name] = reshape_kernel
            maxtext_name = f"max_text_layer/params-decoder-layers_{layer_idx}-self_attention-value-kernel"
            hook_fns[maxtext_name] = reshape_kernel
            maxtext_name = f"max_text_layer/params-decoder-layers_{layer_idx}-self_attention-out-kernel"
            hook_fns[maxtext_name] = reshape_kernel
            for wi_name in ("wi_0", "wi_1"):
                maxtext_wi = f"max_text_layer/params-decoder-layers_{layer_idx}-mlp-{wi_name}-kernel"
                hook_fns[maxtext_wi] = reshape_kernel
            maxtext_wo = f"max_text_layer/params-decoder-layers_{layer_idx}-mlp-wo-kernel"
            hook_fns[maxtext_wo] = reshape_kernel 
            for norm_name in (
                "pre_self_attention_layer_norm-scale",
                "post_self_attention_layer_norm-scale",
            ):
                maxtext_norm = f"max_text_layer/params-decoder-layers_{layer_idx}-{norm_name}"
                hook_fns[maxtext_norm] = reshape_kernel 

    return hook_fns

PARAM_MAPPING = {
    supported_models.GEMMA2_2B: GEMMA2_MAXTEXT_TO_HF_PARAM_MAPPING,
    supported_models.GEMMA2_9B: GEMMA2_MAXTEXT_TO_HF_PARAM_MAPPING,
    supported_models.GEMMA2_27B: GEMMA2_MAXTEXT_TO_HF_PARAM_MAPPING,
    supported_models.LLAMA31_8B: LLAMA31_MAXTEXT_TO_HF_PARAM_MAPPING,
    supported_models.LLAMA31_70B: LLAMA31_MAXTEXT_TO_HF_PARAM_MAPPING,
    supported_models.LLAMA31_405B: LLAMA31_MAXTEXT_TO_HF_PARAM_MAPPING,
}

HOOK_FNS = {
    supported_models.GEMMA2_2B: GEMMA2_MAXTEXT_TO_HF_PARAM_HOOK_FN,
    supported_models.GEMMA2_9B: GEMMA2_MAXTEXT_TO_HF_PARAM_HOOK_FN,
    supported_models.GEMMA2_27B: GEMMA2_MAXTEXT_TO_HF_PARAM_HOOK_FN,
    supported_models.LLAMA31_8B: LLAMA31_MAXTEXT_TO_HF_PARAM_HOOK_FN,
    supported_models.LLAMA31_70B: LLAMA31_MAXTEXT_TO_HF_PARAM_HOOK_FN,
    supported_models.LLAMA31_405B: LLAMA31_MAXTEXT_TO_HF_PARAM_HOOK_FN,
}

