# OWCM Contributor Guide: Adding New Models

This guide explains how to implement and register new channel models in the OWCM library.

## 1. Naming Conventions & Rules

To maintain consistency, all models must adhere to the following rules:

### A. Identifiers
-   **Environment IDs**: Fixed set (`atmospheric`, `indoor`, `underwater`, `underground`, `space`).
-   **Category IDs**: Fixed set per environment (see `registry.md`). Examples: `attenuation`, `turbulence`, `pointing`.
-   **Model IDs**: Lowercase `snake_case`. Contain **NO** units or symbols.
    -   ✅ `gamma_gamma`, `beer_lambert`
    -   ❌ `gamma_gamma_db`, `BeerLambert`
-   **Recipe IDs**: Lowercase `snake_case`. `mvp` must always exist for every environment.

### B. Immutability
-   Once a **Model ID** is released in `registry.md`, it should not change.
-   If you modify the logic significantly, prefer creating a new Versioned ID (e.g., `kim_v2`) or a new descriptive ID.

## 2. Implementation Steps

To add a new model (e.g., a new turbulence model for atmospheric):

### Step 1: Create the Model Class
Go to the appropriate subdirectory, e.g., `owcm/atmospheric/models/turbulence.py`.

Implement a class with the following signature:
1.  Decorate with `@register_model`.
2.  Implement `__init__`, `gain`, `sample`, and `describe`.

```python
import numpy as np
from ...core.types import Link, Environment
from ...core.registry import register_model
from ...core.rng import get_rng

@register_model("atmospheric", "turbulence", "my_new_model")
class MyNewTurbulence:
    """
    Description of the physics or empirical source.
    """
    def __init__(self, link: Link, env: Environment, **kwargs):
        # Extract specific parameters from kwargs with defaults
        self.param_a = kwargs.get("new_param_a", 1.0)
        
    def gain(self, link: Link, env: Environment, rng=None):
        # Return deterministic gain (or mean gain) -> float [0.0, 1.0]
        # Use link properties: link.range_m, link.tx.wavelength_nm, etc.
        return 1.0 

    def sample(self, link: Link, env: Environment, n: int, rng=None):
        # Return n stochastic samples -> np.ndarray of shape (n,)
        rng = get_rng(rng)
        # Example: Normal distribution
        return rng.normal(loc=1.0, scale=0.1, size=n)

    def describe(self):
        # Return metadata for the .describe() report
        return {
            "name": "MyNewTurbulence",
            "param_a": self.param_a
        }
```

### Step 2: Export the Model (Optional but Recommended)
Ensure your file is imported in the environment's `__init__.py` so the decorator runs.
e.g. in `owcm/atmospheric/models/__init__.py`:
```python
from .turbulence import MyNewTurbulence
```

### Step 3: Register in a Recipe (Optional)
If you want users to use this model by default, add or update a recipe in `owcm/atmospheric/recipes.py`:

```python
register_recipe("atmospheric", "my_custom_recipe", {
    "geometry": "uniform_aperture",
    "attenuation": "kim",
    "turbulence": "my_new_model",  # <--- Your new model
    "pointing": "rayleigh_gaussian"
})
```

## 3. Usage

Users can now use your model via the builder:

```python
ch = Channel.environment("atmospheric") \
            .defaults("mvp") \
            .model("turbulence", "my_new_model") \
            .build(new_param_a=5.0)
```

## 4. Checklist
- [ ] Model ID is snake_case and unique in its Category.
- [ ] `__init__` extracts parameters from `kwargs` (does not rely on positional args).
- [ ] `gain()` returns a scalar float (usually <= 1.0).
- [ ] `sample(n)` returns a numpy array of size `n`.
- [ ] `describe()` returns a JSON-serializable dict.
- [ ] Added to `registry.md` documentation.
