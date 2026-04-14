import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model
from ...core.rng import get_rng

@register_model("atmospheric", "turbulence", "lognormal")
class LogNormalTurbulence:
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.sigma_R2 = kwargs.get("sigma_R2", 0.1)
    def gain(self, link: Link, env: Environment, rng=None): return 1.0
    def sample(self, link: Link, env: Environment, n: int, rng=None):
        rng = get_rng(rng)
        sigma2 = self.sigma_R2
        mu = -0.5 * sigma2
        return np.exp(rng.normal(mu, np.sqrt(sigma2), n))
    def describe(self): return {"name": "LogNormal"}

@register_model("atmospheric", "turbulence", "gamma_gamma")
class GammaGammaTurbulence:
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.alpha = kwargs.get("gg_alpha", 2.0)
        self.beta = kwargs.get("gg_beta", 2.0)
    def gain(self, link: Link, env: Environment, rng=None): return 1.0
    def sample(self, link: Link, env: Environment, n: int, rng=None):
        rng = get_rng(rng)
        X = rng.gamma(self.alpha, 1.0/self.alpha, n)
        Y = rng.gamma(self.beta, 1.0/self.beta, n)
        return X * Y
    def describe(self): return {"name": "GammaGamma"}

@register_model("atmospheric", "turbulence", "negative_exponential")
class NegativeExponentialTurbulence:
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass
    def gain(self, link: Link, env: Environment, rng=None): return 1.0
    def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError("NegExp not implemented")
    def describe(self): return {"name": "NegativeExponential"}
