import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model
from ...core.special import erf

@register_model("atmospheric", "geometry", "uniform_aperture")
class UniformApertureGeometricLoss:
    """
    Geometric loss for a uniform beam and circular aperture.
    L_geom = (D_R / (D_T + R * theta))^2
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass

    def gain(self, link: Link, env: Environment, rng=None):
        dr = link.rx.aperture_diameter_m
        dt = link.tx.aperture_diameter_m
        r = link.range_m
        theta = link.tx.divergence_angle_rad
        
        # Beam diameter at receiver
        db = dt + r * theta
        
        # Ratio of areas
        loss = (dr / db)**2
        
        return min(loss, 1.0)

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "UniformApertureGeometricLoss", "ref": "FSO_Survey"}

@register_model("atmospheric", "geometry", "gaussian_collected_exact")
class GaussianCollectedFractionExact:
    """
    Exact collected fraction for Gaussian beam.
    A0 = [erf(v)]^2 where v = sqrt(pi/2)*(a/wz) or similar scalar.
    Using user prompt form: [erf( sqrt(2) * a / wz )]^2
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass

    def gain(self, link: Link, env: Environment, rng=None):
        r = link.range_m
        # Approximation of beam radius at distance R
        wz = (link.tx.aperture_diameter_m / 2) + r * link.tx.divergence_angle_rad
        a = link.rx.aperture_diameter_m / 2
        
        val = erf(np.sqrt(2) * a / wz)
        return val**2

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "GaussianCollectedFractionExact"}

@register_model("atmospheric", "geometry", "gaussian_collected_approx")
class GaussianCollectedFractionApprox:
    """
    Approx: A0 = 1 - exp(-2*a^2 / wz^2)
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        pass

    def gain(self, link: Link, env: Environment, rng=None):
        r = link.range_m
        wz = (link.tx.aperture_diameter_m / 2) + r * link.tx.divergence_angle_rad
        a = link.rx.aperture_diameter_m / 2
        
        return 1.0 - np.exp(-2 * (a**2) / (wz**2))

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        return np.full(n, self.gain(link, env))

    def describe(self):
        return {"name": "GaussianCollectedFractionApprox"}
