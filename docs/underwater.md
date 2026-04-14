# Underwater Optical Wireless Channel Models

This document describes the underwater optical wireless communication (UOWC) models implemented in OWCM, based on the updated `FSO_Survey.pdf` (Section VI).

---

## 1. Overview

### 1.1 Propagation Basics

Underwater optical attenuation is modeled with the extinction coefficient:

\[
c(\lambda) = a(\lambda) + b(\lambda)
\]

and Beer–Lambert propagation factor:

\[
L_{pr}(\lambda, z) = e^{-c(\lambda) z}
\]

where:
- \(a(\lambda)\): absorption coefficient
- \(b(\lambda)\): scattering coefficient
- \(c(\lambda)\): extinction coefficient
- \(z\): optical path length in water

### 1.2 Implemented Link Configurations

The library supports the three analytical UOWC link configurations from the survey:

- **LoS link**
- **Modulating retroreflector link**
- **Reflective (NLoS) link**

---

## 2. Available Models

### 2.1 Extinction Models (`underwater/models/all_models.py`)

#### `a_plus_b` (category: `extinction`)

Beer–Lambert gain:

\[
H = e^{-cR}, \quad c = a+b
\]

Input options:
- `attenuation_c` directly, or
- `attenuation_a` and `attenuation_b` (summed internally)

#### `c_direct` (category: `extinction`)

Alias of `a_plus_b`.

#### `none` placeholders

- `scattering: none`
- `pointing: none`

These contribute gain \(=1\) and are useful for simple recipes.

### 2.2 Survey Analytical Link Models (`underwater/models/survey_model.py`)

#### `los_case` (category: `link`) — LoS

Implements survey LoS received-power model:

\[
P_{R,\text{LoS}} = P_T \eta_T \eta_R L_{pr}\!\left(\lambda,\frac{d}{\cos\theta}\right)
\frac{A_{rec}\cos\theta}{2\pi d^2(1-\cos\theta_0)}
\]

Model returns normalized gain \(P_R/P_T\).

#### `retroreflective_case` (category: `link`) — Retroreflector

Implements survey retroreflector configuration:

\[
P_{R,\text{retro}} =
P_T \eta_T \eta_R \eta_{retro}
L_{pr}\!\left(\lambda,\frac{2d}{\cos\theta}\right)
\left[\frac{A_{retro}\cos\theta}{2\pi d^2(1-\cos\theta_0)}\right]
\left[\frac{A_{rec}\cos\theta}{\pi(d\tan\theta_{0,\text{retro}})^2}\right]
\]

Model returns normalized gain \(P_R/P_T\).

#### `reflective_case` (category: `nlos`) — Reflective NLoS

Implements the piecewise reflective (water–air interface) model from the survey:

\[
P_{R,\text{ref}} \approx A_{rec} f_{R,\text{ref}}(\phi)
\]

with Fresnel-region handling below/above critical angle.

---

## 3. Recipes

Configured in `owcm/underwater/recipes.py`:

| Recipe | Components | Use case |
|---|---|---|
| `beer_lambert` | `extinction=a_plus_b`, `scattering=none`, `pointing=none` | Pure attenuation model |
| `los_link` | `link=los_case` | Analytical LoS link budget |
| `retro_link` | `link=retroreflective_case` | Analytical retroreflector link |
| `reflective_link` | `nlos=reflective_case` | Analytical reflective NLoS link |

---

## 4. Parameter Reference

All parameters are passed via `.build(**kwargs)`.

### 4.1 Common Builder Parameters

| Parameter | Unit | Default | Description |
|---|---:|---:|---|
| `distance_m` | m | 1000.0 | Tx–Rx distance \(d\) |
| `DR_m` | m | 0.1 | Rx aperture diameter |
| `pt_dbm` | dBm | 0.0 | Tx power in dBm |
| `pt_w` | W | — | Tx power in W (overrides `pt_dbm`) |
| `wavelength_nm` | nm | 1550.0 | Wavelength |

### 4.2 Extinction Parameters (`a_plus_b` / `c_direct`)

| Parameter | Unit | Default | Meaning |
|---|---:|---:|---|
| `attenuation_c` | 1/m | 0.05 | Extinction coefficient \(c\) |
| `attenuation_a` | 1/m | — | Absorption \(a\) |
| `attenuation_b` | 1/m | — | Scattering \(b\), where \(c=a+b\) |

### 4.3 LoS / Retro Link Parameters

| Parameter | Unit | Default | Used in | Meaning |
|---|---:|---:|---|---|
| `theta_rad` | rad | 0.0 | LoS, Retro | Off-axis angle \(\theta\) |
| `theta0_rad` | rad | 0.174 | LoS, Retro | Beam divergence half-angle \(\theta_0\) |
| `etaT` | — | 0.9 | LoS, Retro, Reflective | Tx optical efficiency |
| `etaR` | — | 0.9 | LoS, Retro, Reflective | Rx optical efficiency |
| `ARetro_m2` | m² | 0.01 | Retro | Retroreflector area |
| `etaRetro` | — | 0.9 | Retro | Retroreflector efficiency |
| `theta0_retro_rad` | rad | 0.01 | Retro | Retro return divergence |
| `attenuation_c` | 1/m | 0.05 | all three | Extinction coefficient |

### 4.4 Reflective Link Parameters

| Parameter | Unit | Default | Meaning |
|---|---:|---:|---|
| `h_m` | m | 10.0 | Tx depth/height term \(h\) |
| `x_m` | m | 10.0 | Rx depth/height term \(x\) |
| `phi_rad` | rad | 0.0 | Reflection incidence variable \(\phi\) |
| `theta_min_rad` | rad | 0.0 | Lower angular bound |
| `theta_max_rad` | rad | \(\pi/4\) | Upper angular bound |
| `n1` | — | 1.33 | Refractive index medium 1 (water) |
| `n2` | — | 1.0 | Refractive index medium 2 (air) |

---

## 5. Usage Examples

### 5.1 Beer–Lambert attenuation only

```python
from owcm import Channel

ch = Channel.environment("underwater").defaults("beer_lambert").build(
    distance_m=25.0,
    attenuation_a=0.10,
    attenuation_b=0.15
)

print("gain:", ch.gain())
print("Pr [W]:", ch.received_power())
```

### 5.2 LoS analytical link

```python
from owcm import Channel
import numpy as np

ch = Channel.environment("underwater").defaults("los_link").build(
    distance_m=30.0,
    DR_m=0.03,
    attenuation_c=0.12,
    theta_rad=np.deg2rad(5.0),
    theta0_rad=np.deg2rad(12.0),
    etaT=0.9,
    etaR=0.85
)

print("LoS gain:", ch.gain())
```

### 5.3 Retroreflector analytical link

```python
from owcm import Channel
import numpy as np

ch = Channel.environment("underwater").defaults("retro_link").build(
    distance_m=20.0,
    DR_m=0.03,
    attenuation_c=0.10,
    theta_rad=np.deg2rad(3.0),
    theta0_rad=np.deg2rad(10.0),
    theta0_retro_rad=np.deg2rad(0.7),
    ARetro_m2=0.02,
    etaT=0.9,
    etaR=0.9,
    etaRetro=0.85
)

print("Retro gain:", ch.gain())
```

### 5.4 Reflective NLoS analytical link

```python
from owcm import Channel
import numpy as np

ch = Channel.environment("underwater").defaults("reflective_link").build(
    DR_m=0.03,
    attenuation_c=0.10,
    h_m=8.0,
    x_m=10.0,
    phi_rad=np.deg2rad(20.0),
    theta_min_rad=np.deg2rad(5.0),
    theta_max_rad=np.deg2rad(45.0),
    n1=1.33,
    n2=1.0
)

print("Reflective gain:", ch.gain())
```

---

## 6. Notes on Model Scope

- `los_link`, `retro_link`, and `reflective_link` already include attenuation inside each model using `attenuation_c`.
- For those recipes, **do not add `extinction` again** unless you explicitly want extra multiplicative loss.
- `beer_lambert` is a compact baseline attenuation model, useful for quick sensitivity sweeps.

---

## 7. References

- `FSO_Survey.pdf`, Section VI (Underwater)
- Equations implemented correspond to extinction and link configurations described in the survey’s underwater analytical modeling section.
