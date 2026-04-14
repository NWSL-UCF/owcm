import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model

@register_model("space", "free_space", "fspl")
class FreeSpacePathLoss:
    """
    FSPL = (lambda / 4 pi R)^2
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass

    def gain(self, link: Link, env: Environment, rng=None):
        k = link.tx.wavelength_nm * 1e-9 / (4 * np.pi * link.range_m)
        return k**2

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "FreeSpacePathLoss"}
