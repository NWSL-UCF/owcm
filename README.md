# OWCM: Optical Wireless Communication Channel Model Library

**OWCM** is a Pythonic, extensible library for modeling Optical Wireless Communication (OWC) channels across various environments: **Atmospheric (FSO)**, **Indoor (VLC/LiFi)**, **Underwater**, **Underground**, and **Space**.

The library implements a standard taxonomy of channel models (Analytical, Empirical, ML-Enhanced) and creates a unified, composable API for researchers and engineers.

## Features

-   **Multi-Environmental**: Dedicated modules for Atmospheric, Indoor, Underwater, Underground, and Space.
-   **Builder Pattern API**: Fluent interface to configure channels with safe defaults.
-   **Composable Architecture**: Channels are built from independent factors (Geometry × Attenuation × Turbulence × Pointing).
-   **Standard Receipts**: Pre-loaded configurations like `"mvp"`, `"clear_air"`, `"dense_fog"`, `"los"`.
-   **PyPy Friendly**: Pure Python implementation with minimal dependencies (`numpy`, `scipy`).

## Installation

```bash
pip install .
```

## Quick Start

### Atmospheric Channel (FSO)
Simulate a standard 1km link with Kim attenuation and Gamma-Gamma turbulence.

```python
from owcm import Channel

# 1. Build the channel using the 'mvp' recipe
ch = Channel.environment("atmospheric").defaults("mvp").build(
    distance_m=1000, 
    wavelength_nm=1550, 
    pt_w=0.5,            # Transmit power (Watts)
    visibility_km=2.0,   # Visibility for attenuation
    # Additional parameters override defaults
    theta_rad=1e-3,      # Beam divergence
    gg_alpha=3.2,        # Gamma-Gamma alpha
    gg_beta=2.1          # Gamma-Gamma beta
)

# 2. Calculate average Received Power
pr = ch.received_power()
print(f"Received Power: {pr:.3e} W")

# 3. Calculate Outage Probability (P(Pr < threshold))
outage = ch.outage(threshold_w=1e-6, n=100000)
print(f"Outage Probability: {outage:.4f}")
```

### Indoor Channel (VLC)
Simulate a Line-of-Sight (LoS) Lambertian link.

```python
ch_in = Channel.environment("indoor").defaults("los").build(
    distance_m=3.0, 
    lambertian_order=1.0, 
    DR_m=0.01
)
print(f"Indoor Only Gain: {ch_in.gain():.3e}")
```

### Underwater Channel
Beer-Lambert extinction model.

```python
ch_uw = Channel.environment("underwater").defaults("beer_lambert").build(
    distance_m=10.0, 
    attenuation_c=0.1 # Extinction coefficient (1/m)
)
```

## Architecture

The library is structured as follows:

```
OWCM/
  owc/
    core/           # Types, Registry, Composite Logic
    atmospheric/    # FSO Models
    indoor/         # VLC Models
    underwater/     # Underwater Models
    underground/    # Underground Models
    space/          # Space Models
```

Each environment has a `recipes.py` defining default model stacks (e.g., `mvp`, `clear_air`).

## Installation and Reproducibility Environment

OWCM uses Python 3.13 as the reference environment. The package dependencies required for reproducibility are provided in `requirements-reproducibility.txt` with fixed versions:

- NumPy 2.5.4
- SciPy 1.18.1
- Matplotlib 3.11.2
- pytest 9.1.1

To create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

Install the reproducibility dependencies:

```bash
pip install -r requirements-reproducibility.txt
```

Install OWCM:

```bash
pip install -e .
```

The pinned dependency versions are provided to facilitate reproducible installation and execution of the OWCM reference implementation.

Independent atmospheric validation and implementation limits are documented in `docs/external_validation.md`, including comparison with the 6S radiative-transfer model through Py6S.
