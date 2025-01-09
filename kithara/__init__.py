import os
# Allows faster HF download
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

from kithara.dataset import Dataloader
from kithara.preprocessor import Preprocessor, PretrainingPreprocessor, SFTPreprocessor
from kithara.trainer import Trainer
from kithara.callbacks import Checkpointer, Profiler
import jax 
from kithara.utils.gcs_utils import find_cache_root_dir

# Cache JAX compilation to speed up future runs. You should notice
# speedup of training step up on the second run of this script.
jax_cache_dir = os.path.join(find_cache_root_dir(), "jax_cache")
jax.config.update("jax_compilation_cache_dir", os.path.join(find_cache_root_dir(), "jax_cache"))
print(f"Initialized jax_compilation_cache_dir = {jax_cache_dir}")


