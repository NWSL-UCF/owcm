# OWCM Library Tutorial

Welcome to the **OWCM (Optical Wireless Communication Model)** library tutorial. This guide explains how to simulate optical channels across different environments using our composable API.

## Core Concepts

### 1. The Channel Builder
All simulations start with the `Channel` facade. You select an environment, load a default recipe (a pre-configured stack of models), and then build the channel with specific parameters.

```python
from owcm import Channel
ch = Channel.environment("atmospheric").defaults("mvp").build(**params)
```

### 2. Recipes
Recipes are standardized combinations of models. For example, the `mvp` recipe for Atmospheric channels includes:
- **Geometry**: Uniform Aperture Loss
- **Attenuation**: Kim Fog Model
- **Turbulence**: Gamma-Gamma
- **Pointing**: Rayleigh Jitter + Gaussian Loss

### 3. Parameters
Parameters can be passed globally to `.build()`. Standard parameters include:
- `distance_m`: Link range (meters)
- `wavelength_nm`: Optical wavelength (nanometers)
- `pt_w` or `pt_dbm`: Transmit power

---

## Environment 1: Atmospheric (FSO)

### Use Case
Free-space optical links between buildings or towers. Major impairments are fog (attenuation), turbulence (scintillation), and pointing errors.

### Implementation
- **Attenuation**: Uses visibility (km) to calculate loss coefficient (Kim/Kruse/Beer-Lambert).
- **Turbulence**: Uses Gamma-Gamma fading (requires alpha/beta parameters).
- **Pointing**: Statistical jitter model.

### Key Parameters
| Parameter | Description | Default |
| :--- | :--- | :--- |
| `visibility_km` | Atmospheric visibility (affects attenuation) | 2.0 |
| `gg_alpha` | Gamma-Gamma alpha (large scale variance) | 2.0 |
| `gg_beta` | Gamma-Gamma beta (small scale variance) | 2.0 |
| `jitter_sigma_m` | Pointing jitter standard deviation (m) | 0.01 |
| `wz_eq_m` | Equivalent beam width at receiver (m) | 0.1 |
| `theta_rad` | Beam divergence (radians) | 0.001 |
| `DT_m`, `DR_m` | Tx/Rx aperture diameters (m) | 0.05, 0.1 |

---

## Environment 2: Indoor (VLC/LiFi)

### Use Case
Short-range links inside rooms using LED sources. Dominant factors are geometry (Lambertian) and blocking.

### Implementation
- **LoS**: Lambertian emission pattern.
- **NLoS**: "KBounce" (placeholder for reflections).
- **Blockage**: "OnOff" or "Markov" models.

### Key Parameters
| Parameter | Description | Default |
| :--- | :--- | :--- |
| `lambertian_order` | Mode number $m$ (related to semi-angle) | 1.0 |
| `fov_rad` | Receiver Field of View (radians) | $\pi/2$ |

---

## Environment 3: Underwater

### Use Case
Communication between divers, subs, or sensor nodes. Water clarity (turbidity) is the main factor.

### Implementation
- **Extinction**: Uses $c = a + b$ coefficient.
- **Scattering**: Currently simplified or ignored in `beer_lambert` recipe.

### Key Parameters
| Parameter | Description | Default |
| :--- | :--- | :--- |
| `attenuation_c` | Total extinction coefficient ($m^{-1}$) | 0.05 |
| `attenuation_a` | Absorption coefficient (optional) | - |
| `attenuation_b` | Scattering coefficient (optional) | - |

---

## Environment 4: Underground

### Use Case
Mines and tunnels. Challenges include dust and irregular geometry.

### Implementation
- **Dust**: Visibility-like extinction model for dust concentration.
- **LoS**: Simple geometric decay.

### Key Parameters
| Parameter | Description | Default |
| :--- | :--- | :--- |
| `dust_conc_mg_m3` | Dust mass concentration (mg/m³) | 0.0 |

---

## Environment 5: Space

### Use Case
Satellite-to-satellite (ISL) or Deep Space links. Loss is dominated by diffractive spreading (Free Space Path Loss).

### Implementation
- **FSPL**: Fris transmission equation $\left(\frac{\lambda}{4\pi R}\right)^2$.
- **Gains**: Diffraction limited Tx gain, Telescope Rx gain.

### Key Parameters
| Parameter | Description | Default |
| :--- | :--- | :--- |
| `distance_m` | Often very large (e.g., GEO distances) | - |
