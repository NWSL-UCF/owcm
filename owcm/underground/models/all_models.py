import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model
from ...core.common_models import NoLossModel


@register_model("underground", "los", "lambertian_los")
class UndergroundLoS:
    """
    Simple 1/R^2 LoS gain for underground VLC, approximating Lambertian LoS
    behavior in tunnels (survey Eq. 57, with geometry simplified to 1/d^2).
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass

    def gain(self, link: Link, env: Environment, rng=None):
        r2 = link.range_m**2 + 1e-9
        return 1.0 / r2

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "UndergroundLoS", "approx": "1/R^2"}


@register_model("underground", "dust", "exp_extinction")
class DustExtinction:
    """
    Exponential dust attenuation: H = exp(-k * C * R)
    where C is dust concentration (mg/m^3) and k is a specific extinction coeff.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        # Dust concentration in mg/m^3 (can also come from env.params)
        self.mass_conc = kwargs.get(
            "dust_conc_mg_m3",
            env.params.get("dust_conc_mg_m3", 0.0),
        )
        # Specific extinction coefficient per mg/m^3 (tunable)
        self.k = kwargs.get(
            "dust_k_per_m_per_mg_m3",
            env.params.get("dust_k_per_m_per_mg_m3", 0.5),
        )

    def gain(self, link: Link, env: Environment, rng=None):
        loss_coeff = self.k * self.mass_conc
        return float(np.exp(-loss_coeff * link.range_m))

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {
            "name": "DustExtinction",
            "model": "exp(-k * C * R)",
            "k_per_m_per_mg_m3": self.k,
        }


@register_model("underground", "dust", "none")
class NoDust(NoLossModel):
    pass


@register_model("underground", "blockage", "none")
class NoBlockage(NoLossModel):
    pass


@register_model("underground", "blockage", "onoff")
class OnOffBlockage:
    """
    Binary blockage model for underground tunnels.
    gain() returns mean (1 - p_blocked); sample() returns 0/1 sequence.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.p_blocked = float(
            kwargs.get("p_blocked", env.params.get("p_blocked", 0.1))
        )

    def gain(self, link: Link, env: Environment, rng=None):
        return 1.0 - self.p_blocked

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        rng = np.random.default_rng(rng)
        unblocked = 1.0 - rng.binomial(1, self.p_blocked, size=n)
        return np.asarray(unblocked, dtype=float)

    def describe(self):
        return {
            "name": "UndergroundOnOffBlockage",
            "p_blocked": self.p_blocked,
        }


@register_model("underground", "blockage", "markov")
class MarkovBlockage:
    """
    Two-state Markov blockage (blocked / unblocked), suitable for machinery
    and moving obstacles in mines.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.p_01 = float(kwargs.get("p_01", env.params.get("p_01", 0.1)))
        self.p_10 = float(kwargs.get("p_10", env.params.get("p_10", 0.3)))
        denom = self.p_01 + self.p_10
        self.p_unblocked_ss = self.p_10 / denom if denom > 0 else 0.5

    def gain(self, link: Link, env: Environment, rng=None):
        return self.p_unblocked_ss

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        rng = np.random.default_rng(rng)
        out = np.empty(n)
        state = 0  # 0 = unblocked, 1 = blocked
        for i in range(n):
            out[i] = 0.0 if state else 1.0
            u = rng.random()
            if state == 0:
                state = 1 if u < self.p_01 else 0
            else:
                state = 0 if u < self.p_10 else 1
        return out

    def describe(self):
        return {
            "name": "UndergroundMarkovBlockage",
            "p_01": self.p_01,
            "p_10": self.p_10,
            "steady_state_unblocked": self.p_unblocked_ss,
        }


@register_model("underground", "multipath", "none")
class NoMultipath(NoLossModel):
    pass


@register_model("underground", "multipath", "kbounce")
class KBounce(NoLossModel):
    """
    Placeholder for underground K-bounce NLoS; currently behaves as no-loss
    multiplier (1.0). Extend with detailed tunnel-wall reflections as needed.
    """
    pass
