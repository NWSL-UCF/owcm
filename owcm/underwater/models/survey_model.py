import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model

def c_lambda(a_lambda: float, b_lambda: float) -> float:
    return a_lambda + b_lambda

def L_pr(c: float, z: float) -> float:
    return float(np.exp(-c * z))

# -------------------------
# LoS (Eq 89)
# -------------------------
@register_model("underwater", "link", "los_case")
class TableXILoS:
    """
    Exact implementation of Table XI Eq. 89 (LoS).
    Gain = PR / PT.
    Internal attenuation: exp(-c * d / cos(theta))
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.theta = kwargs.get("theta_rad", 0.0)      # Off-axis angle
        self.theta0 = kwargs.get("theta0_rad", 0.174)  # 10 deg half-angle default
        self.etaT = kwargs.get("etaT", 0.9)
        self.etaR = kwargs.get("etaR", 0.9)
        
        # c can come from kwargs OR env
        if "attenuation_c" in kwargs:
             self.c = kwargs["attenuation_c"]
        elif "attenuation_c" in env.params:
             self.c = env.params["attenuation_c"]
        else:
             self.c = 0.05 # default

    def gain(self, link: Link, env: Environment, rng=None):
        PT = 1.0 # Normalized for Gain calculation
        d = link.range_m
        Arec = link.rx.aperture_diameter_m**2 * np.pi / 4
        
        if np.cos(self.theta) <= 0:
            return 0.0

        z = d / np.cos(self.theta)
        L = L_pr(self.c, z)
        denom = 2 * np.pi * (d**2) * (1 - np.cos(self.theta0))
        if denom <= 0: return 0.0
        
        PR = PT * self.etaT * self.etaR * L * Arec * np.cos(self.theta) / denom
        return PR

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "TableXILoS", "eqn": "89"}

# -------------------------
# Retro (Eq 90)
# -------------------------
@register_model("underwater", "link", "retroreflective_case")
class TableXIRetro:
    """
    Exact implementation of Table XI Eq. 90 (Retroreflector).
    Gain = PR / PT.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.theta = kwargs.get("theta_rad", 0.0)
        self.theta0 = kwargs.get("theta0_rad", 0.174)
        self.theta0_retro = kwargs.get("theta0_retro_rad", 0.01) # Narrow return
        self.etaT = kwargs.get("etaT", 0.9)
        self.etaR = kwargs.get("etaR", 0.9)
        self.etaRetro = kwargs.get("etaRetro", 0.9)
        self.ARetro = kwargs.get("ARetro_m2", 0.01) # Area of retroreflector
        
        if "attenuation_c" in kwargs: self.c = kwargs["attenuation_c"]
        elif "attenuation_c" in env.params: self.c = env.params["attenuation_c"]
        else: self.c = 0.05

    def gain(self, link: Link, env: Environment, rng=None):
        PT = 1.0
        d = link.range_m
        Arec = link.rx.aperture_diameter_m**2 * np.pi / 4
        
        ct = np.cos(self.theta)
        if ct <= 0:
            return 0.0

        den1 = (1 - np.cos(self.theta0))
        den2 = np.tan(self.theta0_retro)
        if den1 <= 0 or abs(den2) < 1e-12:
            return 0.0

        z = 2 * d / ct
        L = L_pr(self.c, z)

        term1 = (self.ARetro * ct) / (2 * np.pi * d**2 * den1)
        term2 = (Arec * ct) / (np.pi * (d * den2)**2)
        
        PR = PT * self.etaT * self.etaR * self.etaRetro * L * term1 * term2
        return PR

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "TableXIRetro", "eqn": "90"}

# -------------------------
# Reflective NLoS (Eq 91-92)
# -------------------------
@register_model("underwater", "nlos", "reflective_case")
class TableXIReflective:
    """
    Exact implementation of Table XI Eq. 91-92 (Reflective).
    Uses strict geometric definitions (h, x, phi).
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.h = kwargs.get("h_m", 10.0)
        self.x = kwargs.get("x_m", 10.0)
        self.phi = kwargs.get("phi_rad", 0.0) # Angle of incidence?? User said phi is angular variable.
        # User note: "phi is an angular variable... implementation can be exact only if simulation defines these geometrically"
        # We accept phi as input.
        
        self.theta_min = kwargs.get("theta_min_rad", 0.0)
        self.theta_max = kwargs.get("theta_max_rad", np.pi/4)
        self.n1 = kwargs.get("n1", 1.33)
        self.n2 = kwargs.get("n2", 1.0)
        self.etaT = kwargs.get("etaT", 0.9)
        self.etaR = kwargs.get("etaR", 0.9)
        
        if "attenuation_c" in kwargs: self.c = kwargs["attenuation_c"]
        elif "attenuation_c" in env.params: self.c = env.params["attenuation_c"]
        else: self.c = 0.05

    def gain(self, link: Link, env: Environment, rng=None):
        PT = 1.0
        Arec = link.rx.aperture_diameter_m**2 * np.pi / 4
        
        z = self.h + self.x
        L = L_pr(self.c, z)
        
        denom = 2 * np.pi * (z**3) * (np.cos(self.theta_min) - np.cos(self.theta_max))
        if denom <= 0: return 0.0
        
        if self.phi < self.theta_min or self.phi > self.theta_max:
             return 0.0
             
        cphi = np.cos(self.phi)
        if cphi <= 0:
            return 0.0
            
        common = PT * self.etaT * self.etaR * L * cphi / denom
        
        theta_c = float(np.arcsin(self.n2 / self.n1))
        
        # Use stable boundary: Case 2 for phi >= theta_c
        if self.phi >= theta_c:
            f_val = common
        else:
            val = (self.n1 / self.n2) * np.sin(self.phi)
            val = np.clip(val, -1.0, 1.0)
            theta_t = float(np.arcsin(val))
            
            t_plus = np.tan(theta_t + self.phi)
            t_minus = np.tan(theta_t - self.phi)
            s_plus = np.sin(self.phi + theta_t)
            s_minus = np.sin(self.phi - theta_t)
            
            term1 = 0.0 if abs(t_plus) < 1e-12 else (t_minus / t_plus)**2
            term2 = 0.0 if abs(s_plus) < 1e-12 else (s_minus / s_plus)**2
            fresnel = 0.5 * (term1 + term2)
            
            f_val = common * fresnel
            
        PR = Arec * f_val
        return PR

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "TableXIReflective", "eqn": "91-92"}
