import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model

@register_model("atmospheric", "attenuation", "beer_lambert")
class BeerLambertAttenuation:
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.alpha = kwargs.get("alpha", 0.0)
    def gain(self, link: Link, env: Environment, rng=None):
        return np.exp(-self.alpha * link.range_m)
    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))
    def describe(self): return {"name": "BeerLambert", "alpha": self.alpha}

@register_model("atmospheric", "attenuation", "kim")
class KimFogModel:
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.visibility_km = kwargs.get("visibility_km", 2.0)
        self.wl_nm = link.tx.wavelength_nm
    def _calculate_q(self, v_km):
        if v_km > 50: return 1.6
        elif 6 < v_km <= 50: return 1.3
        elif 1 < v_km <= 6: return 0.16 * v_km + 0.34
        elif 0.5 < v_km <= 1: return v_km - 0.5
        else: return 0.0
    def gain(self, link: Link, env: Environment, rng=None):
        q = self._calculate_q(self.visibility_km)
        alpha_km = (3.91 / self.visibility_km) * ((self.wl_nm / 550.0) ** (-q))
        return np.exp(-(alpha_km/1000.0) * link.range_m)
    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))
    def describe(self): return {"name": "KimFogModel"}

@register_model("atmospheric", "attenuation", "kruse")
class KruseFogModel:
    """
    Standard Kruse model: q depends on V but simpler logic.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.visibility_km = kwargs.get("visibility_km", 2.0)
        self.wl_nm = link.tx.wavelength_nm
    def gain(self, link: Link, env: Environment, rng=None):
        v = self.visibility_km
        # q logic for Kruse
        if v > 50: q = 1.6
        elif 6 < v <= 50: q = 1.3
        else: q = 0.585 * (v**(1/3))
        
        alpha_km = (3.91 / v) * ((self.wl_nm / 550.0) ** (-q))
        return np.exp(-(alpha_km/1000.0) * link.range_m)
        
    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))
    def describe(self): return {"name": "KruseFogModel"}

# # Placeholders for others specified in registry
# @register_model("atmospheric", "attenuation", "al_naboulsi_convection")
# class AlNaboulsiConvection:
#     def __init__(self, link: Link, env: Environment, **kwargs): pass
#     def gain(self, link: Link, env: Environment, rng=None): raise NotImplementedError
#     def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError
#     def describe(self): return {}

# @register_model("atmospheric", "attenuation", "al_naboulsi_advection")
# class AlNaboulsiAdvection:
#     def __init__(self, link: Link, env: Environment, **kwargs): pass
#     def gain(self, link: Link, env: Environment, rng=None): raise NotImplementedError
#     def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError
#     def describe(self): return {}

# @register_model("atmospheric", "attenuation", "ijaz")
# class IjazFog:
#     def __init__(self, link: Link, env: Environment, **kwargs): pass
#     def gain(self, link: Link, env: Environment, rng=None): raise NotImplementedError
#     def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError
#     def describe(self): return {}

# @register_model("atmospheric", "attenuation", "esmail")
# class EsmailFog:
#     def __init__(self, link: Link, env: Environment, **kwargs): pass
#     def gain(self, link: Link, env: Environment, rng=None): raise NotImplementedError
#     def sample(self, link: Link, env: Environment, n: int, rng=None): raise NotImplementedError
#     def describe(self): return {}


# --- small helpers (keep local so these classes are self-contained) ---

_DB_PER_NP = 4.343  # 10/log(10)

def _get_distance_m(link, **kwargs) -> float:
    """
    Try common link distance fields used in OWCM.
    Fallback: allow passing distance_m explicitly in kwargs.
    """
    for attr in ("distance_m", "range_m", "R", "distance", "range"):
        if hasattr(link, attr):
            val = getattr(link, attr)
            if val is not None:
                return float(val)
    if "distance_m" in kwargs:
        return float(kwargs["distance_m"])
    raise ValueError("Distance not found. Provide link.distance_m (or pass distance_m=...).")

def _get_wavelength_um(link, **kwargs) -> float:
    """
    Table V formulas use wavelength in micrometers (µm).
    Accept wavelength_um directly OR wavelength_nm and convert.
    """
    if "wavelength_um" in kwargs and kwargs["wavelength_um"] is not None:
        return float(kwargs["wavelength_um"])

    if "wavelength_nm" in kwargs and kwargs["wavelength_nm"] is not None:
        return float(kwargs["wavelength_nm"]) / 1000.0

    for attr in ("wavelength_um", "lambda_um"):
        if hasattr(link, attr):
            val = getattr(link, attr)
            if val is not None:
                return float(val)

    for attr in ("wavelength_nm", "lambda_nm", "wavelength"):
        if hasattr(link, attr):
            val = getattr(link, attr)
            if val is not None:
                # assume nm if it's like 850/1550; if it's ~1.55, it's probably µm already
                v = float(val)
                return v / 1000.0 if v > 10 else v

    raise ValueError("Wavelength not found. Provide wavelength_um or wavelength_nm.")

def _get_visibility_km(env, **kwargs) -> float:
    """
    Visibility V in km (required by all 4 models).
    """
    if "visibility_km" in kwargs and kwargs["visibility_km"] is not None:
        return float(kwargs["visibility_km"])
    for attr in ("visibility_km", "V_km", "visibility"):
        if hasattr(env, attr):
            val = getattr(env, attr)
            if val is not None:
                return float(val)
    raise ValueError("visibility_km is required for fog attenuation models.")

def _gain_from_A_db_per_km(A_db_per_km: float, distance_m: float) -> float:
    # convert dB/km -> Np/m -> exp(-alpha*R)
    alpha_np_per_m = (A_db_per_km / _DB_PER_NP) / 1000.0
    return float(np.exp(-alpha_np_per_m * distance_m))


# -------------------------
# Al Naboulsi (Convection)
# A = 4.343 * (0.11478*λ + 3.8367) / V
# λ in µm, V in km (Table V)
# -------------------------
@register_model("atmospheric", "attenuation", "al_naboulsi_convection")
class AlNaboulsiConvection:
    def __init__(self, link, env, **kwargs):
        self._V_km = _get_visibility_km(env, **kwargs)
        self._lam_um = _get_wavelength_um(link, **kwargs)

    def _A_db_per_km(self) -> float:
        V = self._V_km
        lam = self._lam_um
        if V <= 0:
            raise ValueError("visibility_km must be > 0.")
        return _DB_PER_NP * (0.11478 * lam + 3.8367) / V  # from Table V

    def gain(self, link, env, rng=None):
        R = _get_distance_m(link)
        A = self._A_db_per_km()
        return _gain_from_A_db_per_km(A, R)

    def sample(self, link, env, n: int, rng=None):
        g = self.gain(link, env)
        return np.full(int(n), g, dtype=float)

    def describe(self):
        return {
            "name": "Al Naboulsi Convection Fog",
            "formula_db_per_km": "A = 4.343*(0.11478*λ + 3.8367)/V",
            "lambda_units": "µm",
            "visibility_units": "km",
        }


# -------------------------
# Al Naboulsi (Advection)
# A = 4.343 * (0.18126*λ^2 + 0.13709*λ + 3.7502) / V
# λ in µm, V in km (Table V)
# -------------------------
@register_model("atmospheric", "attenuation", "al_naboulsi_advection")
class AlNaboulsiAdvection:
    def __init__(self, link, env, **kwargs):
        self._V_km = _get_visibility_km(env, **kwargs)
        self._lam_um = _get_wavelength_um(link, **kwargs)

    def _A_db_per_km(self) -> float:
        V = self._V_km
        lam = self._lam_um
        if V <= 0:
            raise ValueError("visibility_km must be > 0.")
        return _DB_PER_NP * (0.18126 * lam**2 + 0.13709 * lam + 3.7502) / V

    def gain(self, link, env, rng=None):
        R = _get_distance_m(link)
        A = self._A_db_per_km()
        return _gain_from_A_db_per_km(A, R)

    def sample(self, link, env, n: int, rng=None):
        g = self.gain(link, env)
        return np.full(int(n), g, dtype=float)

    def describe(self):
        return {
            "name": "Al Naboulsi Advection Fog",
            "formula_db_per_km": "A = 4.343*(0.18126*λ^2 + 0.13709*λ + 3.7502)/V",
            "lambda_units": "µm",
            "visibility_units": "km",
        }


# -------------------------
# Ijaz (Controlled Fog)
# A = (17/V) * (λ/0.55)^(-q(λ))
# q(λ) = 0.1428*λ - 0.0947
# λ in µm, V in km (Table V)
# -------------------------
@register_model("atmospheric", "attenuation", "ijaz")
class IjazFog:
    def __init__(self, link, env, **kwargs):
        self._V_km = _get_visibility_km(env, **kwargs)
        self._lam_um = _get_wavelength_um(link, **kwargs)

    def _q(self) -> float:
        lam = self._lam_um
        return 0.1428 * lam - 0.0947

    def _A_db_per_km(self) -> float:
        V = self._V_km
        lam = self._lam_um
        if V <= 0:
            raise ValueError("visibility_km must be > 0.")
        q = self._q()
        return (17.0 / V) * (lam / 0.55) ** (-q)

    def gain(self, link, env, rng=None):
        R = _get_distance_m(link)
        A = self._A_db_per_km()
        return _gain_from_A_db_per_km(A, R)

    def sample(self, link, env, n: int, rng=None):
        g = self.gain(link, env)
        return np.full(int(n), g, dtype=float)

    def describe(self):
        return {
            "name": "Ijaz Controlled Fog",
            "formula_db_per_km": "A = (17/V) * (λ/0.55)^(-q(λ)),  q(λ)=0.1428λ-0.0947",
            "lambda_units": "µm",
            "visibility_units": "km",
        }


# -------------------------
# Esmail (Unified Fog Regression)
# A = k * V^(-(a*λ + b))
# Table V gives the structure but NOT the fitted constants.
# So we require k, a, b from kwargs (or env).
# -------------------------
@register_model("atmospheric", "attenuation", "esmail")
class EsmailFog:
    def __init__(self, link, env, **kwargs):
        self._V_km = _get_visibility_km(env, **kwargs)
        self._lam_um = _get_wavelength_um(link, **kwargs)

        # Table V shows the model form A = k * V^{-(aλ + b)} but not the constants.
        # Users must provide them.
        self._k = kwargs.get("k", getattr(env, "esmail_k", None))
        self._a = kwargs.get("a", getattr(env, "esmail_a", None))
        self._b = kwargs.get("b", getattr(env, "esmail_b", None))

        if self._k is None or self._a is None or self._b is None:
            raise ValueError(
                "EsmailFog requires parameters k, a, b (from the Esmail regression). "
                "Pass k=..., a=..., b=... when building the channel."
            )

        self._k = float(self._k)
        self._a = float(self._a)
        self._b = float(self._b)

    def _A_db_per_km(self) -> float:
        V = self._V_km
        lam = self._lam_um
        if V <= 0:
            raise ValueError("visibility_km must be > 0.")
        exponent = -(self._a * lam + self._b)
        return self._k * (V ** exponent)

    def gain(self, link, env, rng=None):
        R = _get_distance_m(link)
        A = self._A_db_per_km()
        return _gain_from_A_db_per_km(A, R)

    def sample(self, link, env, n: int, rng=None):
        g = self.gain(link, env)
        return np.full(int(n), g, dtype=float)

    def describe(self):
        return {
            "name": "Esmail Unified Fog Regression",
            "formula_db_per_km": "A = k * V^(-(a*λ + b))",
            "lambda_units": "µm",
            "visibility_units": "km",
            "k": self._k,
            "a": self._a,
            "b": self._b,
        }
