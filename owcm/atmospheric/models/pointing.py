import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model
from ...core.rng import get_rng

@register_model("atmospheric", "pointing", "rayleigh_gaussian")
class RayleighGaussianPointingLoss:
    """
    Combined model:
    1. Jitter r is Rayleigh distributed (sigma_s).
    2. Loss L = exp(-2r^2 / w_eq^2).
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.jitter_sigma = kwargs.get("jitter_sigma_m", 0.01)
        self.w_eq = kwargs.get("wz_eq_m", 0.1) 

    def gain(self, link: Link, env: Environment, rng=None):
        # Mean gain
        v = (self.w_eq**2) / (self.w_eq**2 + 4 * self.jitter_sigma**2)
        return v

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        rng = get_rng(rng)
        r = rng.rayleigh(self.jitter_sigma, n)
        loss = np.exp(-2 * (r**2) / (self.w_eq**2))
        return loss

    def describe(self):
        return {"name": "RayleighGaussianPointingLoss"}

@register_model("atmospheric", "pointing", "none")
class NoPointingLoss:
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass
    def gain(self, link: Link, env: Environment, rng=None): return 1.0
    def sample(self, link: Link, env: Environment, n: int, rng=None): return np.ones(n)
    def describe(self): return {"name": "NoPointingLoss"}

# Placeholders for future phase
@register_model("atmospheric", "pointing", "hoyt_gaussian")
class HoytGaussianPointingLoss:
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass
    def gain(self, link: Link, env: Environment, rng=None): raise NotImplementedError("Hoyt pointing not implemented yet")
    def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError
    def describe(self): return {"name": "HoytGaussian"}

@register_model("atmospheric", "pointing", "beckmann_gaussian")
class BeckmannGaussianPointingLoss:
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass
    def gain(self, link: Link, env: Environment, rng=None): raise NotImplementedError("Beckmann pointing not implemented yet")
    def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError
    def describe(self): return {"name": "BeckmannGaussian"}
