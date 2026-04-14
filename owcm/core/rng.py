import numpy as np
from typing import Optional, Union

def get_rng(rng: Optional[Union[np.random.Generator, int]] = None) -> np.random.Generator:
    """Standardizes RNG creation."""
    if rng is None:
        return np.random.default_rng()
    if isinstance(rng, int):
        return np.random.default_rng(rng)
    return rng
