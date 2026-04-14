import numpy as np
from ...core.types import Link, Environment, ChannelModel
from ...core.registry import register_model

@register_model("space", "deepspace", "table_xiii")
class DeepSpaceTableXIII:
    def __init__(self, link: Link, env: Environment, **kwargs):
        self.w0_rad = kwargs.get("w0_rad")
        if self.w0_rad is None:
             # It is required, but if not provided, maybe raise error or handle in gain params?
             # The request says required.
             pass
        self.gamma_r = kwargs.get("gamma_r", 0.0)
        self.sigma_p = kwargs.get("sigma_p", 0.0)
        self.p0 = kwargs.get("p0", 1.0)
        self.La = kwargs.get("La", 1.0)
        self.Ls = kwargs.get("Ls", 1.0)
        self.Lb = kwargs.get("Lb", 1.0)
        self.eta_t = kwargs.get("eta_t", 0.9)
        self.eta_r = kwargs.get("eta_r", 0.9)

    def gain(self, link: Link, env: Environment, rng=None) -> float:
        # Inputs
        # Read from Link
        R = link.range_m
        if R == 0:
            return 0.0 # Avoid division by zero, though unlikely in deep space
            
        lambda_nm = link.tx.wavelength_nm
        lambda_m = lambda_nm * 1e-9
        
        # Power is calculated in P_r equation, but gain is Pr/Pt.
        # Pt is in Watts.
        
        # Link params
        Dr = link.rx.aperture_diameter_m
        
        # Kwargs overrides? The class assumes they are static or passed in init.
        # If I need to support changing them per call, I'd need to check kwargs again?
        # Standard channel models usually take params in init.
        
        # (113) Free-space loss L_fs
        # L_fs = (lambda / (4 * pi * R))^2
        L_fs = (lambda_m / (4 * np.pi * R))**2
        
        # (114) Transmitter gain G_t
        # G_t = 8 / w0^2
        if self.w0_rad is None:
             raise ValueError("w0_rad (beam divergence) is required for DeepSpaceTableXIII")
        G_t = 8.0 / (self.w0_rad**2)
        
        # (115) Receiver gain G_r
        # G_r = (pi * Dr / lambda)^2 * (1 - gamma_r^2)
        G_r = ((np.pi * Dr) / lambda_m)**2 * (1.0 - self.gamma_r**2)
        
        # (116) Pointing loss L_pt
        # Equation (5): L_pt = p0^(w0^2 / (4*sigma_p^2))
        if self.sigma_p <= 0:
            L_pt = 1.0
        else:
            exponent = self.w0_rad**2 / (4.0 * self.sigma_p**2)
            L_pt = self.p0 ** exponent
            
        # (112) Received power Pr
        # Pr = Pt * Gt * Gr * Lfs * La * Ls * Lb * Lpt * eta_t * eta_r
        # Gain H = Pr / Pt
        # H = Gt * Gr * Lfs * La * Ls * Lb * Lpt * eta_t * eta_r
        
        H = G_t * G_r * L_fs * self.La * self.Ls * self.Lb * L_pt * self.eta_t * self.eta_r
        
        return H

    def sample(self, link: Link, env: Environment, n: int = 1, rng=None) -> np.ndarray:
        val = self.gain(link, env, rng)
        return np.full(n, val)

    def describe(self) -> dict:
        return {
            "name": "DeepSpaceTableXIII",
            "description": "Deep Space Optical Channel Model (Table XIII)",
            "equations": {
                "L_fs": "(lambda / (4*pi*R))^2",
                "G_t": "8 / w0^2",
                "G_r": "(pi*Dr/lambda)^2 * (1 - gamma_r^2)",
                "L_pt": "(w0/(4*sigma_p))^2 * p0",
                "H": "Gt * Gr * Lfs * La * Ls * Lb * Lpt * eta_t * eta_r"
            },
            "parameters": {
                "w0_rad": self.w0_rad,
                "gamma_r": self.gamma_r,
                "sigma_p": self.sigma_p,
                "p0": self.p0,
                "La": self.La,
                "Ls": self.Ls,
                "Lb": self.Lb,
                "eta_t": self.eta_t,
                "eta_r": self.eta_r
            }
        }
