from typing import Any, Dict, List, Optional, Union
import numpy as np

from .core.types import ChannelModel, Link, Environment, Tx, Rx, Results
from .core.composite import CompositeChannel
from .core.registry import get_model, list_models, list_environments
from .core.defaults import get_recipe
from .core.rng import get_rng
from .core.validate import normalize_wavelength, validate_positive

class ConfiguredChannel:
    """
    The final object the user interacts with.
    Wraps a Link, Environment, and the CompositeChannel model.
    """
    def __init__(self, link: Link, env: Environment, model: CompositeChannel):
        self.link = link
        self.env = env
        self.model = model

    def gain(self, rng=None) -> Union[float, np.ndarray]:
        """Returns deterministic or instantaneous gain."""
        rng = get_rng(rng)
        return self.model.gain(self.link, self.env, rng=rng)

    def sample(self, n: int, rng=None) -> np.ndarray:
        """Returns n samples of channel gain."""
        rng = get_rng(rng)
        return self.model.sample(self.link, self.env, n, rng=rng)

    def received_power(self, rng=None) -> Union[float, np.ndarray]:
        """Calculates Pr = Pt * gain."""
        g = self.gain(rng=rng)
        # Tx power is in dBm in types.py, need to convert?
        # Wait, types.py says Pt_dbm. Let's assume linear watts for calculation if we want Pr in Watts.
        # But types.py Tx has power_dbm.
        pt_watts = 10**(self.link.tx.power_dbm / 10.0) * 1e-3
        return pt_watts * g

    def received_power_samples(self, n: int, rng=None) -> np.ndarray:
        """Samples Pr."""
        g = self.sample(n, rng=rng)
        pt_watts = 10**(self.link.tx.power_dbm / 10.0) * 1e-3
        return pt_watts * g

    def outage(self, threshold_w: float, n: int = 100000, rng=None) -> float:
        """Calculates outage probability P(Pr < threshold)."""
        samples = self.received_power_samples(n, rng=rng)
        return np.mean(samples < threshold_w)

    def describe(self) -> Dict[str, Any]:
        return {
            "environment": self.env.name,
            "link": {
                "range_m": self.link.range_m,
                "wavelength_nm": self.link.tx.wavelength_nm
            },
            "model": self.model.describe()
        }

class EnvironmentBuilder:
    """
    Fluent builder to configure the channel.
    channel = Channel.environment("atmospheric").defaults("mvp").build(...)
    """
    def __init__(self, env_name: str):
        self.env_name = env_name
        self._recipe: Dict[str, str] = {} # category -> model_name
        self._params: Dict[str, Any] = {} # kwargs for build

    def list_models(self) -> Dict[str, List[str]]:
        return list_models(self.env_name)

    def defaults(self, recipe_name: str) -> "EnvironmentBuilder":
        """Loads a default recipe for this environment."""
        recipe_config = get_recipe(self.env_name, recipe_name)
        self._recipe.update(recipe_config)
        return self

    def model(self, category: str, model_name: str) -> "EnvironmentBuilder":
        """Overrides a specific model component."""
        self._recipe[category] = model_name
        return self

    def build(self, **kwargs) -> ConfiguredChannel:
        """
        Constructs the channel.
        kwargs are used to:
          1. Configure Link/Environment (distance, wavelength, apertures, etc.)
          2. Configure individual Models (alpha, beta, visibility, etc.)
        """
        
        # 1. Parse Link/Tx/Rx parameters from kwargs or defaults
        # We need to extract specific keys for Link/Tx/Rx.
        # For simplicity in this phase, we'll maintain a list of known keys or just strict mapping.
        
        # Tx defaults
        tx = Tx(
            power_dbm=kwargs.get("pt_dbm", 0.0), # or 'pt_w' conversion?
            # User request example used pt_w=0.5. Let's support both or standardized.
            # Example: pt_w=0.5 -> 27 dBm.
            wavelength_nm=kwargs.get("wavelength_nm", 1550.0),
            divergence_angle_rad=kwargs.get("theta_rad", 1e-3),
            aperture_diameter_m=kwargs.get("DT_m", 0.05)
        )
        if "pt_w" in kwargs:
             # overwrites power_dbm
             tx.power_dbm = 10 * np.log10(kwargs["pt_w"] / 1e-3)

        # Rx defaults
        rx = Rx(
            aperture_diameter_m=kwargs.get("DR_m", 0.1),
            field_of_view_rad=kwargs.get("fov_rad", np.pi/2),
            sensitivity_dbm=kwargs.get("sens_dbm", -30.0)
        )
        # Position logic implementation (simple distance-based)
        distance = kwargs.get("distance_m", 1000.0)
        validate_positive(distance, "distance_m")
        rx.position = np.array([0.0, 0.0, distance])
        
        link = Link(tx, rx)
        
        # Environment metadata
        env = Environment(name=self.env_name, params=kwargs)
        
        # 2. Instantiate models based on recipe
        # We iterate through the recipe {category: model_name}
        # and instantiate each model class with (link, env, **kwargs)
        # The model constructors must extract their own params from kwargs.
        
        factor_models = []
        for category, model_name in self._recipe.items():
            constructor = get_model(self.env_name, category, model_name)
            if constructor is None:
                raise ValueError(f"Model '{model_name}' (category '{category}') not found in registry for environment '{self.env_name}'.")
            
            # Instantiate
            # Note: models might expect 'env' or 'link' explicitly or just kwargs.
            # We will pass them conceptually.
            # Standard signature: Model(link, env, **kwargs) purely?
            # Or Model(**kwargs) and use link/env in methods?
            # User plan didn't strictly specify constructor signature, but recommended "accept (link, env, **params)".
            
            instance = constructor(link, env, **kwargs)
            factor_models.append(instance)

        composite = CompositeChannel(factor_models)
        
        return ConfiguredChannel(link, env, composite)


class Channel:
    """Public facade."""
    
    @staticmethod
    def environment(name: str) -> EnvironmentBuilder:
        return EnvironmentBuilder(name)

    @staticmethod
    def list_environments() -> List[str]:
        return list_environments()
