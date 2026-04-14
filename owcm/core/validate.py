import numpy as np
from typing import Optional

def validate_positive(value, name):
    if np.any(np.array(value) <= 0):
        # Allow 0? "positive" usually > 0.
        # Physics inputs like distance usually > 0.
        raise ValueError(f"{name} must be positive, got {value}")
    return value

def normalize_wavelength(w: float) -> float:
    if w > 100:
        return w * 1e-9
    return w

def validate_fov(fov_rad: float):
    if fov_rad <= 0 or fov_rad > np.pi:
        raise ValueError(f"FOV must be in (0, pi], got {fov_rad}")

def validate_model_id(env_name: str, category: str, model_id: str, registry_lookup):
    """
    Checks if model exists in registry.
    registry_lookup: function(env, cat, id) -> constructor or None
    """
    if registry_lookup(env_name, category, model_id) is None:
        raise ValueError(f"Model ID '{model_id}' not found for environment '{env_name}', category '{category}'.")
