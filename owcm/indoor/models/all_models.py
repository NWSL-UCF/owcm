"""
Indoor OWC channel models per FSO_Survey.pdf Section V.

- LoS: Lambertian model with irradiance/incidence angles, concentrator, FOV
- NLoS: K-bounce diffuse reflections
- Blockage: On-off and Markov chain models
"""
import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model
from ...core.common_models import NoLossModel


# ---------------------------------------------------------------------------
# Lambertian LoS (Eq 27–31, FSO_Survey Section V.C)
# H_LoS = (Ad/d²) * Ro(φ₀) * cos(ω₀) * Ts(ω₀) * g(ω₀),  ω ≤ ωc
# Ro(φ) = (m+1)/(2π) cos^m(φ),  m = -ln2/ln(cos(φ₁/₂))
# g(ω) = n²/sin²(ωc) for 0 ≤ ω ≤ ωc
# ---------------------------------------------------------------------------
@register_model("indoor", "los", "lambertian_los")
class IndoorLambertianLoS:
    """
    Lambertian LoS channel gain for indoor VLC/OWC [FSO_Survey Eq 27–31].
    Supports irradiance angle φ, incidence angle ω, FOV, and concentrator gain.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        # Lambertian order: m = -ln2 / ln(cos(φ₁/₂)) or provide m directly
        semi_rad = kwargs.get("semi_angle_half_power_rad", None)
        self.m = kwargs.get("lambertian_order", None)
        if self.m is None and semi_rad is not None:
            c = np.cos(semi_rad)
            self.m = -np.log(2) / np.log(max(c, 1e-9)) if c > 0 else 1.0
        if self.m is None:
            self.m = 1.0
        # Concentrator: g(ω) = n²/sin²(ωc)
        self.n_refractive = kwargs.get("concentrator_refractive_index", 1.0)
        # Optional filter gain Ts (default 1)
        self.filter_gain = kwargs.get("optical_filter_gain", 1.0)

    def _cos_phi_omega(self, link: Link, env: Environment) -> tuple:
        """Return (cos_phi, cos_omega). Use kwargs if provided, else aligned (1,1)."""
        cos_phi = env.params.get("cos_phi") or env.params.get("cos_irradiance")
        cos_omega = env.params.get("cos_psi") or env.params.get("cos_incidence")
        if cos_phi is not None and cos_omega is not None:
            return float(cos_phi), float(cos_omega)
        # Compute from positions: assume Tx points toward Rx, Rx toward Tx
        d = link.rx.position - link.tx.position
        r = np.linalg.norm(d)
        if r < 1e-12:
            return 1.0, 1.0
        u = d / r  # unit Tx->Rx
        # Aligned: both normals parallel to u -> cos_phi = cos_omega = 1
        return 1.0, 1.0

    def gain(self, link: Link, env: Environment, rng=None) -> float:
        r = link.range_m
        if r < 1e-12:
            return 0.0
        Ad = np.pi * (link.rx.aperture_diameter_m / 2) ** 2
        omega_c = link.rx.field_of_view_rad  # half-angle FOV
        cos_phi, cos_omega = self._cos_phi_omega(link, env)

        # Rect: 0 if ω > ωc (i.e. cos(ω) < cos(ωc))
        if cos_omega < np.cos(omega_c) - 1e-9:
            return 0.0

        # Ro(φ) = (m+1)/(2π) cos^m(φ)
        Ro = (self.m + 1) / (2 * np.pi) * (max(cos_phi, 0.0) ** self.m)
        # g(ω) = n²/sin²(ωc)
        sin_omega_c = np.sin(omega_c)
        g = (self.n_refractive ** 2) / (sin_omega_c ** 2) if sin_omega_c > 1e-12 else 1.0
        Ts = self.filter_gain

        # H = (Ad/d²) * Ro * cos(ω) * Ts * g
        H = (Ad / (r ** 2)) * Ro * cos_omega * Ts * g
        return max(0.0, float(H))

    def sample(self, link: Link, env: Environment, n: int, rng=None) -> np.ndarray:
        g = self.gain(link, env, rng)
        return np.full(n, g)

    def describe(self) -> dict:
        return {
            "name": "IndoorLambertianLoS",
            "ref": "FSO_Survey Eq 27-31",
            "lambertian_order": self.m,
        }


@register_model("indoor", "los", "lambertian_los_plus_nlos")
class IndoorLambertianLoSPlusNLoS:
    """
    Combined LoS + NLoS gain [FSO_Survey Eq 37]: H = H_LoS + H_NLoS.
    Use with nlos="none" for physically correct additive behavior.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self._los = IndoorLambertianLoS(link, env, **kwargs)
        self._nlos = KBounceNLoS(link, env, **kwargs)

    def gain(self, link: Link, env: Environment, rng=None) -> float:
        h_los = self._los.gain(link, env, rng)
        h_nlos = self._nlos.gain(link, env, rng)
        return h_los + h_nlos

    def sample(self, link: Link, env: Environment, n: int, rng=None) -> np.ndarray:
        g = self.gain(link, env, rng)
        return np.full(n, g)

    def describe(self) -> dict:
        return {
            "name": "IndoorLambertianLoSPlusNLoS",
            "ref": "FSO_Survey Eq 37",
        }


# ---------------------------------------------------------------------------
# NLoS: K-bounce diffuse (Eq 32–36, FSO_Survey Section V.C)
# dH1_NLoS for single-bounce; recursive for multi-bounce
# ---------------------------------------------------------------------------
@register_model("indoor", "nlos", "none")
class NoNLoS(NoLossModel):
    pass


def _get_room_params(env: Environment, link: Link, kwargs: dict) -> dict:
    """Extract room parameters for NLoS models."""
    params = env.params.copy()
    params.update(kwargs)
    return {
        "rho": params.get("reflectance", params.get("rho", 0.7)),
        "room_area_m2": params.get("room_area_m2", 25.0),
        "n_bounces": int(params.get("n_bounces", params.get("K", 1))),
    }


@register_model("indoor", "nlos", "kbounce")
class KBounceNLoS:
    """
    K-bounce diffuse NLoS channel gain [FSO_Survey Eq 32–36].
    Uses first-bounce approximation: dH1 = Ad/(dSk² dRk²) * Ro(φSk) * ρ * ΔA *
        cos(ωSk) * cos(φRk) * cos(ωRk) * Ts * g
    For multiple bounces, applies effective path-length scaling.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        p = _get_room_params(env, link, kwargs)
        self.rho = p["rho"]
        self.room_area = p["room_area_m2"]
        self.K = p["n_bounces"]
        self.m = kwargs.get("lambertian_order", 1.0)
        self.n_refractive = kwargs.get("concentrator_refractive_index", 1.0)
        self.filter_gain = kwargs.get("optical_filter_gain", 1.0)
        # Effective reflector distance: assume ceiling ~ half room dimension
        self.ceiling_height_m = kwargs.get("ceiling_height_m", np.sqrt(self.room_area) * 0.6)

    def _single_bounce_gain(self, link: Link, env: Environment) -> float:
        """First-bounce diffuse approximation (Eq 36)."""
        d0 = link.range_m
        if d0 < 1e-9:
            return 0.0
        Ad = np.pi * (link.rx.aperture_diameter_m / 2) ** 2
        omega_c = link.rx.field_of_view_rad
        # Simplified geometry: reflector at ceiling, d_Sk ≈ d_Rk ≈ d0/2 for single bounce
        d_eff = max(self.ceiling_height_m, d0 * 0.5)
        d_Sk = d_Rk = d_eff
        delta_A = self.room_area / 4  # effective reflector patch
        cos_omega_Sk = 1.0  # assume normal incidence on ceiling
        cos_phi_Rk = 1.0
        cos_omega_Rk = 1.0
        if cos_omega_Rk < np.cos(omega_c) - 1e-9:
            return 0.0
        Ro = (self.m + 1) / (2 * np.pi)
        sin_wc = np.sin(omega_c)
        g = (self.n_refractive ** 2) / (sin_wc ** 2) if sin_wc > 1e-12 else 1.0
        Ts = self.filter_gain
        dH1 = (
            Ad
            / (d_Sk ** 2 * d_Rk ** 2)
            * Ro
            * self.rho
            * delta_A
            * cos_omega_Sk
            * cos_phi_Rk
            * cos_omega_Rk
            * Ts
            * g
        )
        return max(0.0, float(dH1))

    def gain(self, link: Link, env: Environment, rng=None) -> float:
        # Sum contributions: first bounce dominates; higher bounces scaled by rho^(k-1)
        h1 = self._single_bounce_gain(link, env)
        total = 0.0
        rho_k = 1.0
        for k in range(1, min(self.K + 1, 5)):
            total += h1 * rho_k
            rho_k *= self.rho
        return total

    def sample(self, link: Link, env: Environment, n: int, rng=None) -> np.ndarray:
        g = self.gain(link, env, rng)
        return np.full(n, g)

    def describe(self) -> dict:
        return {
            "name": "KBounceNLoS",
            "ref": "FSO_Survey Eq 32-36",
            "n_bounces": self.K,
            "reflectance": self.rho,
        }


# ---------------------------------------------------------------------------
# Blockage: On-off and Markov [FSO_Survey Section V.D]
# ---------------------------------------------------------------------------
@register_model("indoor", "blockage", "none")
class NoBlockage(NoLossModel):
    pass


@register_model("indoor", "blockage", "onoff")
class OnOffBlockage:
    """
    Binary blockage: gain is 0 (blocked) or 1 (unblocked) with probability p_blocked.
    gain() returns mean (1 - p_blocked). sample() returns Bernoulli samples.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.p_blocked = float(
            kwargs.get("p_blocked", env.params.get("p_blocked", 0.1))
        )

    def gain(self, link: Link, env: Environment, rng=None) -> float:
        return 1.0 - self.p_blocked

    def sample(self, link: Link, env: Environment, n: int, rng=None) -> np.ndarray:
        rng = np.random.default_rng(rng)
        unblocked = 1.0 - rng.binomial(1, self.p_blocked, size=n)
        return np.asarray(unblocked, dtype=float)

    def describe(self) -> dict:
        return {
            "name": "OnOffBlockage",
            "ref": "FSO_Survey Section V.D",
            "p_blocked": self.p_blocked,
        }


@register_model("indoor", "blockage", "markov")
class MarkovBlockage:
    """
    Markov-chain blockage: two states (blocked/unblocked) with transition probs.
    p_01 = P(unblocked -> blocked), p_10 = P(blocked -> unblocked).
    gain() returns steady-state unblocked probability. sample() generates Markov chain.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.p_01 = float(kwargs.get("p_01", env.params.get("p_01", 0.1)))
        self.p_10 = float(kwargs.get("p_10", env.params.get("p_10", 0.3)))
        # Steady-state P(unblocked) = p_10 / (p_01 + p_10)
        denom = self.p_01 + self.p_10
        self.p_unblocked_ss = self.p_10 / denom if denom > 0 else 0.5

    def gain(self, link: Link, env: Environment, rng=None) -> float:
        return self.p_unblocked_ss

    def sample(self, link: Link, env: Environment, n: int, rng=None) -> np.ndarray:
        rng = np.random.default_rng(rng)
        out = np.empty(n)
        state = 0  # 0=unblocked, 1=blocked
        for i in range(n):
            out[i] = 0.0 if state else 1.0
            u = rng.random()
            if state == 0:
                state = 1 if u < self.p_01 else 0
            else:
                state = 0 if u < self.p_10 else 1
        return out

    def describe(self) -> dict:
        return {
            "name": "MarkovBlockage",
            "ref": "FSO_Survey Section V.D",
            "p_01": self.p_01,
            "p_10": self.p_10,
            "steady_state_unblocked": self.p_unblocked_ss,
        }
