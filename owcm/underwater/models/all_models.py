import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model
from ...core.common_models import NoLossModel

@register_model("underwater", "extinction", "a_plus_b")
class UnderwaterExtinction:
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass
    def gain(self, link: Link, env: Environment, rng=None):
        c = 0.05
        if "attenuation_c" in env.params: c = env.params["attenuation_c"]
        elif "attenuation_a" in env.params and "attenuation_b" in env.params:
            c = env.params["attenuation_a"] + env.params["attenuation_b"]
        return np.exp(-c * link.range_m)
    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))
    def describe(self): return {"name": "UnderwaterExtinction"}

@register_model("underwater", "extinction", "c_direct")
class CDirectExtinction(UnderwaterExtinction): pass

@register_model("underwater", "scattering", "none")
class NoScattering(NoLossModel): pass

@register_model("underwater", "pointing", "none")
class NoPointing(NoLossModel): pass

@register_model("underwater", "pointing", "gaussian")
class GaussianPointing:
    def __init__(self, *args, **kwargs): pass
    def gain(self, *args): raise NotImplementedError
    def sample(self, *args, **kwargs): raise NotImplementedError
    def describe(self): return {}
