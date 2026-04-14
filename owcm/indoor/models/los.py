import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model

@register_model("indoor", "analytical", "lambertian_los")
class IndoorLambertianLoS:
    """
    Standard Lambertian LoS gain.
    H = (m+1)A / (2pi D^2) * cos^m(phi) * cos(psi) * Rect(psi/FOV)
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.mode_order = kwargs.get("lambertian_order", 1.0) # m = -ln2 / ln(cos(half_power))

    def gain(self, link: Link, env: Environment, rng=None):
        r = link.range_m
        if r == 0: return 0.0
        
        # Geometry: assuming Tx pointing down, Rx pointing up?
        # Or simple cosine model based on positions.
        # User Phase 1: simple functionality.
        # Let's assume ideal alignment or provide cos_phi, cos_psi in kwargs?
        # Better: calculate from vectors. 
        # For Phase 1 MVP, user probably supplies simple dot products or angles, OR we assume aligned z-axis.
        # Simplified: H = (m+1)A_eff / (2pi R^2)
        
        m = self.mode_order
        Ar = link.rx.aperture_diameter_m**2 * np.pi / 4
        
        # Using simplified LoS for now (aligned)
        h = (m + 1) * Ar / (2 * np.pi * r**2)
        return h

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "IndoorLambertianLoS"}
