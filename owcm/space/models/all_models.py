import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model
from ...core.common_models import NoLossModel

@register_model("space", "free_space", "fspl")
class FSPL:
    def __init__(self, link: Link, env: Environment, **kwargs): pass
    def gain(self, link: Link, env: Environment, rng=None):
        k = link.tx.wavelength_nm * 1e-9 / (4 * np.pi * link.range_m)
        return k**2
    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))
    def describe(self): return {"name": "FSPL"}

@register_model("space", "tx_gain", "diffraction_limited")
class DiffLimitedTx:
    def __init__(self, link: Link, env: Environment, **kwargs): pass
    def gain(self, link: Link, env: Environment, rng=None): return 1.0 # Placeholder
    def sample(self, link: Link, env: Environment, n: int, rng=None): return np.ones(n)
    def describe(self): return {"name": "DiffLimitedTx"}

@register_model("space", "rx_gain", "telescope")
class TelescopeRx:
    def __init__(self, link: Link, env: Environment, **kwargs): pass
    def gain(self, link: Link, env: Environment, rng=None): return 1.0 # Placeholder
    def sample(self, link: Link, env: Environment, n: int, rng=None): return np.ones(n)
    def describe(self): return {"name": "TelescopeRx"}

@register_model("space", "pointing", "none")
class NoPointing(NoLossModel): pass

@register_model("space", "pointing", "gaussian")
class GaussianPointing:
    def __init__(self, link: Link, env: Environment, **kwargs): pass
    def gain(self, link: Link, env: Environment, rng=None): raise NotImplementedError
    def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError
    def describe(self): return {}

@register_model("space", "atmospheric_entry", "none")
class NoAtm(NoLossModel): pass

@register_model("space", "atmospheric_entry", "beer_lambert")
class BeerLambertSpace:
    def __init__(self, link: Link, env: Environment, **kwargs): pass
    def gain(self, link: Link, env: Environment, rng=None): raise NotImplementedError
    def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError
    def describe(self): return {}

@register_model("space", "link_budget", "multiplicative_chain")
class LinkBudgetChain:
    """Identity model (1.0) since Composite already does the multiplication."""
    def __init__(self, link: Link, env: Environment, **kwargs): pass
    def gain(self, link: Link, env: Environment, rng=None): return 1.0
    def sample(self, link: Link, env: Environment, n: int, rng=None): return np.ones(n)
    def describe(self): return {"name": "LinkBudgetChain"}
