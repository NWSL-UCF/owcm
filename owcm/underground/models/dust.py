import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model

@register_model("underground", "dust", "exp_extinction")
class DustAerosolExtinctionModel:
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.mass_conc = kwargs.get("dust_conc_mg_m3", 0.0)

    def gain(self, link: Link, env: Environment, rng=None):
        # H = exp(-k * C * R) ?
        # simplified visibility-like model
        k = 0.5 # placeholder specific extinction coeff per mg/m3
        loss_coeff = k * self.mass_conc
        return np.exp(-loss_coeff * link.range_m)

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "DustAerosolExtinctionModel"}

@register_model("underground", "los", "lambertian_los")
class UndergroundLoSLambertian:
    # Reusing similar logic to indoor, or alias?
    # Better to keep separate for environment spec.
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass
    def gain(self, link: Link, env: Environment, rng=None):
        # Simple 1/R^2 decay
        return 1.0 / (link.range_m**2 + 1e-9)
    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))
    def describe(self): 
        return {"name": "UndergroundLoS"}
