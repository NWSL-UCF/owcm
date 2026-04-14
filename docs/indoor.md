# Indoor Optical Wireless Channel Models

This document describes the indoor OWC/VLC channel models implemented in OWCM, based on the taxonomy and analytical formulations in *FSO_Survey.pdf* (Section V). The indoor environment covers Visible Light Communication (VLC), Wireless Infrared Communication (WIRC), and general indoor optical links with Line-of-Sight (LoS), Non-Line-of-Sight (NLoS), and blockage effects.

---

## 1. Overview

### 1.1 Link Configurations

Indoor optical channels support several link types (per survey Section V.B):

| Configuration    | Description                                                | Typical Use            |
|------------------|------------------------------------------------------------|------------------------|
| **Directed LoS** | Highly directional; strict alignment                       | WIRC, high data rate   |
| **Non-Directed LoS** | Wide aperture; no strict alignment                     | VLC, mobility          |
| **Diffused**     | Ceiling/wall reflections; no direct LoS required           | Diffuse IR             |
| **Tracked**      | Beam tracking for mobile terminals                         | High-rate WIRC         |

### 1.2 Channel Structure

The indoor composite channel multiplies three categories:

- **LoS** – Line-of-sight path gain
- **NLoS** – Non-line-of-sight (diffuse reflections)
- **Blockage** – Human/obstacle shadowing

For the combined LoS+NLoS model (`lambertian_los_plus_nlos`), the total channel gain is *additive*:

\[
H = H_{\text{LoS}} + H_{\text{NLoS}}
\]

Blockage then multiplies the total: \(H_{\text{total}} = (H_{\text{LoS}} + H_{\text{NLoS}}) \times H_{\text{blockage}}\).

---

## 2. Available Models

### 2.1 LoS Models

#### `lambertian_los`

Lambertian LoS channel gain [FSO_Survey Eq 27–31]:

\[
H_{\text{LoS}} = \frac{A_d}{d^2} \, R_o(\phi_0) \, \cos(\omega_0) \, T_s(\omega_0) \, g(\omega_0), \quad \omega_0 \leq \omega_c
\]

where:

- \(R_o(\phi) = \frac{m+1}{2\pi} \cos^m(\phi)\) – Lambertian radiant intensity
- \(m = -\ln 2 / \ln(\cos \phi_{1/2})\) – Lambertian order
- \(g(\omega) = n^2 / \sin^2(\omega_c)\) – Optical concentrator gain
- \(\omega_c\) – Receiver field-of-view (half-angle)
- \(T_s\) – Optical filter gain
- \(A_d\) – Photodiode active area
- \(d\) – Link distance

Out of FOV: \(H_{\text{LoS}} = 0\) when \(\omega_0 > \omega_c\).

#### `lambertian_los_plus_nlos`

Combined LoS + NLoS gain [FSO_Survey Eq 37]:

\[
H = H_{\text{LoS}} + H_{\text{NLoS}}
\]

Use with `nlos="none"` in the recipe. Designed for `room_mvp` and `room_full` recipes.

---

### 2.2 NLoS Models

#### `none`

No NLoS contribution. Gain = 1 (multiplicative pass-through in the composite).

#### `kbounce`

K-bounce diffuse reflection model [FSO_Survey Eq 32–36]. First-bounce approximation:

\[
dH^{(1)}_{\text{NLoS}} = \frac{A_d}{d_{Sk}^2 \, d_{Rk}^2} \, R_o(\phi_{Sk}) \, \rho \, \Delta A \, \cos(\omega_{Sk}) \, \cos(\phi_{Rk}) \, \cos(\omega_{Rk}) \, T_s \, g
\]

Multi-bounce contributions are scaled by \(\rho^{k-1}\) for bounce order \(k\).

---

### 2.3 Blockage Models

#### `none`

No blockage. Gain = 1.

#### `onoff`

Binary blockage: gain is 0 (blocked) or 1 (unblocked).

- **`gain()`** – mean gain = \(1 - p_{\text{blocked}}\)
- **`sample()`** – Bernoulli samples (0 or 1)

#### `markov`

Two-state Markov chain (blocked / unblocked).

- **`gain()`** – steady-state unblocked probability:
  \[
  P(\text{unblocked}) = \frac{p_{10}}{p_{01} + p_{10}}
  \]
- **`sample()`** – correlated Markov chain samples

---

## 3. Parameter Reference

### 3.1 Link / Transmitter / Receiver (passed to `build()`)

| Parameter        | Symbol   | Unit | Default   | Description                                |
|------------------|----------|------|-----------|--------------------------------------------|
| `distance_m`     | \(d\)    | m    | 1000.0    | Tx–Rx separation                           |
| `wavelength_nm`  | \(\lambda\) | nm | 1550.0 | Optical wavelength                         |
| `pt_dbm`         | –        | dBm  | 0.0       | Transmit power (dBm)                       |
| `pt_w`           | \(P_t\)  | W    | –         | Transmit power (W); overrides `pt_dbm`     |
| `DR_m`           | \(D_R\)  | m    | 0.1       | Receiver aperture diameter                 |
| `fov_rad`        | \(\omega_c\) | rad | \(\pi/2\) | Receiver FOV half-angle                    |
| `DT_m`           | \(D_T\)  | m    | 0.05      | Transmitter aperture diameter              |
| `theta_rad`      | –        | rad  | 1e-3      | Beam divergence half-angle                 |
| `sens_dbm`       | –        | dBm  | -30.0     | Receiver sensitivity                       |

### 3.2 Lambertian LoS Parameters

| Parameter                      | Symbol   | Unit | Default | Description                                      |
|--------------------------------|----------|------|---------|--------------------------------------------------|
| `lambertian_order`             | \(m\)    | –    | 1.0     | Lambertian order                                 |
| `semi_angle_half_power_rad`    | \(\phi_{1/2}\) | rad | –   | Semi-angle at half power; used to compute \(m\) if `lambertian_order` is not set |
| `concentrator_refractive_index`| \(n\)    | –    | 1.0     | Concentrator refractive index                    |
| `optical_filter_gain`          | \(T_s\)  | –    | 1.0     | Optical filter gain                              |
| `cos_phi` / `cos_irradiance`   | \(\cos\phi\) | – | –   | Irradiance cosine (Tx normal → link direction)   |
| `cos_psi` / `cos_incidence`    | \(\cos\omega\) | – | –   | Incidence cosine (Rx normal → link direction)    |

If `cos_phi` and `cos_psi` are omitted, perfect alignment (\(\cos\phi = \cos\omega = 1\)) is assumed.

### 3.3 NLoS (K-Bounce) Parameters

| Parameter           | Symbol   | Unit | Default              | Description                          |
|---------------------|----------|------|----------------------|--------------------------------------|
| `reflectance`       | \(\rho\) | –    | 0.7                  | Surface reflection coefficient       |
| `rho`               | \(\rho\) | –    | 0.7                  | Alias for `reflectance`              |
| `room_area_m2`      | –        | m²   | 25.0                 | Room floor area                      |
| `n_bounces`         | \(K\)    | –    | 1                    | Number of diffuse bounces            |
| `K`                 | \(K\)    | –    | 1                    | Alias for `n_bounces`                |
| `ceiling_height_m`  | –        | m    | \(\approx 0.6\sqrt{A}\) | Ceiling height for reflector distance |
| `lambertian_order`  | \(m\)    | –    | 1.0                  | Same as LoS                          |
| `concentrator_refractive_index` | \(n\) | – | 1.0 | Same as LoS                        |
| `optical_filter_gain` | \(T_s\) | – | 1.0 | Same as LoS                       |

### 3.4 Blockage Parameters

#### On-Off Blockage

| Parameter   | Symbol          | Unit | Default | Description                |
|-------------|-----------------|------|---------|----------------------------|
| `p_blocked` | \(p_{\text{blocked}}\) | – | 0.1 | Probability of blockage   |

#### Markov Blockage

| Parameter | Symbol  | Unit | Default | Description                           |
|-----------|---------|------|---------|---------------------------------------|
| `p_01`    | –       | –    | 0.1     | \(P(\text{unblocked} \to \text{blocked})\)  |
| `p_10`    | –       | –    | 0.3     | \(P(\text{blocked} \to \text{unblocked})\)  |

---

## 4. Recipes

| Recipe      | LoS                  | NLoS | Blockage | Use Case                          |
|-------------|----------------------|------|----------|-----------------------------------|
| `los`       | lambertian_los       | none | none     | Pure LoS only                     |
| `room_mvp`  | lambertian_los_plus_nlos | none | onoff  | LoS+NLoS with on-off blockage     |
| `room_full` | lambertian_los_plus_nlos | none | markov | LoS+NLoS with Markov blockage     |

---

## 5. Usage Examples

### 5.1 Basic Setup

```python
from owcm import Channel

# Build an indoor channel with default "los" recipe
ch = Channel.environment("indoor").defaults("los").build(
    distance_m=2.0,       # 2 m link
    DR_m=0.01             # 1 cm receiver aperture
)

# Channel gain (linear)
gain = ch.gain()
print(f"Channel gain: {gain}")

# Received power (Watts)
Pr = ch.received_power()
print(f"Received power: {Pr} W")
```

### 5.2 Lambertian Order from Semi-Angle

```python
import numpy as np

# LED with 60° semi-angle at half power
ch = Channel.environment("indoor").defaults("los").build(
    distance_m=3.0,
    DR_m=0.01,
    semi_angle_half_power_rad=np.radians(60)  # m computed from this
)
```

### 5.3 Non-Aligned Geometry (Tilted Tx/Rx)

```python
# User provides cos(phi) and cos(psi) for misalignment
ch = Channel.environment("indoor").defaults("los").build(
    distance_m=2.0,
    DR_m=0.01,
    cos_phi=0.9,    # irradiance angle ~26°
    cos_psi=0.85    # incidence angle ~32°
)
```

### 5.4 Room with Diffuse Reflections and Blockage

```python
ch = Channel.environment("indoor").defaults("room_mvp").build(
    distance_m=3.0,
    DR_m=0.01,
    fov_rad=np.pi/2,
    reflectance=0.7,      # wall/ceiling reflectance
    room_area_m2=25.0,
    n_bounces=2,
    p_blocked=0.1         # 10% blockage probability
)

# Mean gain (includes average blockage)
gain = ch.gain()

# Samples with random blockage (0 or 1 per sample)
samples = ch.sample(100)
```

### 5.5 Markov Blockage (Time-Correlated Shadowing)

```python
ch = Channel.environment("indoor").defaults("room_full").build(
    distance_m=2.5,
    DR_m=0.01,
    reflectance=0.6,
    p_01=0.05,   # transition to blocked
    p_10=0.2     # transition to unblocked
)

# Steady-state mean
gain = ch.gain()

# Correlated time series (e.g. for packet-level simulation)
blockage_trace = ch.sample(1000)
```

### 5.6 Custom Model Selection

```python
# Override specific components
ch = Channel.environment("indoor") \
    .defaults("room_mvp") \
    .model("blockage", "markov") \
    .build(
        distance_m=3.0,
        DR_m=0.01,
        p_01=0.1,
        p_10=0.3
    )
```

### 5.7 Outage Probability

```python
# Outage: P(received_power < threshold)
ch = Channel.environment("indoor").defaults("room_mvp").build(
    distance_m=4.0,
    DR_m=0.01,
    pt_w=0.5,
    p_blocked=0.15
)

threshold_watts = 1e-7
p_outage = ch.outage(threshold_watts, n=100_000)
print(f"Outage probability: {p_outage:.4f}")
```

### 5.8 Model Inspection

```python
ch = Channel.environment("indoor").defaults("room_mvp").build(
    distance_m=2.0,
    DR_m=0.01,
    reflectance=0.7
)

info = ch.describe()
print(info)
# {
#   "environment": "indoor",
#   "link": {"range_m": 2.0, "wavelength_nm": 1550.0},
#   "model": {
#     "type": "CompositeChannel",
#     "components": [
#       {"name": "IndoorLambertianLoSPlusNLoS", "ref": "FSO_Survey Eq 37"},
#       {"name": "None"},
#       {"name": "OnOffBlockage", "p_blocked": 0.1}
#     ]
#   }
# }
```

---

## 6. Naming Conventions and `build()` Flow

All parameters are passed to `build(**kwargs)`. The builder uses them to construct:

1. **Tx** – `pt_dbm`, `pt_w`, `wavelength_nm`, `theta_rad`, `DT_m`
2. **Rx** – `DR_m`, `fov_rad`, `sens_dbm`; position set from `distance_m`
3. **Environment** – `params = kwargs` (so model-specific params are available via `env.params`)
4. **Models** – Each model receives `(link, env, **kwargs)` and reads its own parameters from `kwargs` or `env.params`

Use the parameter names from Section 3 when calling `build()`.

---

## 7. Symbol Glossary

| Symbol | Description |
|--------|-------------|
| \(A_d\) | Photodiode active area (m²) |
| \(d\) | Link distance (m) |
| \(m\) | Lambertian emission order |
| \(\phi\) | Irradiance angle (Tx normal to Tx–Rx ray) |
| \(\omega\) | Incidence angle (Rx normal to Rx–Tx ray) |
| \(\phi_{1/2}\) | Semi-angle at half optical power |
| \(\omega_c\) | Receiver field-of-view half-angle |
| \(R_o(\phi)\) | Lambertian radiant intensity |
| \(g(\omega)\) | Optical concentrator gain |
| \(T_s\) | Optical filter gain |
| \(n\) | Concentrator refractive index |
| \(\rho\) | Surface reflectance coefficient |
| \(H_{\text{LoS}}\) | LoS channel DC gain |
| \(H_{\text{NLoS}}\) | NLoS channel DC gain |

---

## 8. References

- **FSO_Survey.pdf** – Section V: Indoor Propagation Models (link configurations, analytical modeling, Lambertian LoS, K-bounce diffuse NLoS, blockage variability)
