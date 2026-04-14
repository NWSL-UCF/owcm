import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model

@register_model("underwater", "analytical", "extinction")
class UnderwaterExtinction:
    """
    H = exp(-c(lambda) * R)
    c = a + b
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass

    def gain(self, link: Link, env: Environment, rng=None):
        # User defined c or a, b?
        # Default Jerlov type I?
        c = 0.05 # default /m (Clear ocean)
        if "attenuation_c" in env.params:
            c = env.params["attenuation_c"]
        elif "attenuation_a" in env.params and "attenuation_b" in env.params:
            c = env.params["attenuation_a"] + env.params["attenuation_b"]
            
        return np.exp(-c * link.range_m)

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "UnderwaterExtinction"}
