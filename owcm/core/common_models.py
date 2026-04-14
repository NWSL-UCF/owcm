import numpy as np
from .types import Link, Environment

class NoLossModel:
    """Base class for 'none' models (gain=1)."""
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass
    def gain(self, link: Link, env: Environment, rng=None): return 1.0
    def sample(self, link: Link, env: Environment, n: int, rng=None): return np.ones(n)
    def describe(self): return {"name": "None"}
