# OWCM API Reference

This document describes the public application programming interface (API) of the Optical Wireless Communication Channel Model (OWCM) library. OWCM provides a unified interface for constructing, evaluating, and sampling optical wireless channel models in atmospheric, indoor, underwater, underground, and space environments.

## 1. Basic Usage

The primary public interface is the `Channel` class:

```python
from owcm import Channel
```

A channel is created by selecting an environment, optionally loading a predefined recipe, optionally overriding individual models, and then supplying the channel parameters through `build()`.

```python
ch = (
    Channel.environment("atmospheric")
    .defaults("mvp")
    .build(
        distance_m=1000.0,
        wavelength_nm=1550.0,
        pt_w=0.5,
        visibility_km=2.0,
        theta_rad=1e-3,
        gg_alpha=3.2,
        gg_beta=2.1,
    )
)
```

The resulting `ConfiguredChannel` object can be used to calculate deterministic/mean gain, generate random channel samples, calculate received power, and estimate outage probability.

---

## 2. Supported Environments

The currently registered environment identifiers are:

| Environment ID | Application |
|---|---|
| `atmospheric` | Terrestrial free-space optical (FSO) propagation |
| `indoor` | Indoor VLC/LiFi and optical wireless links |
| `underwater` | Underwater optical wireless communication |
| `underground` | Underground/tunnel optical wireless communication |
| `space` | Space and deep-space optical communication |

Available environments can be queried programmatically:

```python
Channel.list_environments()
```

---

## 3. Channel Builder API

### `Channel.environment(name)`

Creates an environment-specific channel builder.

```python
builder = Channel.environment("atmospheric")
```

**Parameters**

- `name` (`str`): environment identifier.

**Returns**

- `EnvironmentBuilder`

---

### `EnvironmentBuilder.defaults(recipe_name)`

Loads a predefined combination of channel models for the selected environment.

```python
builder = Channel.environment("atmospheric").defaults("mvp")
```

**Parameters**

- `recipe_name` (`str`): name of a registered recipe.

**Returns**

- The same `EnvironmentBuilder`, allowing method chaining.

---

### `EnvironmentBuilder.model(category, model_name)`

Selects or overrides a model within a channel-model category.

```python
builder = (
    Channel.environment("atmospheric")
    .defaults("mvp")
    .model("attenuation", "kruse")
)
```

**Parameters**

- `category` (`str`): model category.
- `model_name` (`str`): registered model identifier.

**Returns**

- The same `EnvironmentBuilder`.

---

### `EnvironmentBuilder.list_models()`

Returns the models currently registered for an environment.

```python
models = Channel.environment("atmospheric").list_models()
print(models)
```

The returned object is a dictionary mapping model categories to available model identifiers.

---

### `EnvironmentBuilder.build(**kwargs)`

Constructs a `ConfiguredChannel`.

```python
ch = Channel.environment("atmospheric").defaults("mvp").build(
    distance_m=1000.0,
    wavelength_nm=1550.0,
)
```

Parameters supplied through `build()` configure the transmitter, receiver, propagation geometry, environment, and selected component models.

---

## 4. Common Build Parameters

The following parameters are accepted by the common channel builder.

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `distance_m` | Tx–Rx separation | m | `1000.0` |
| `wavelength_nm` | Optical wavelength | nm | `1550.0` |
| `pt_dbm` | Transmitted optical power | dBm | `0.0` |
| `pt_w` | Transmitted optical power; overrides `pt_dbm` when supplied | W | — |
| `theta_rad` | Transmitter beam-divergence parameter | rad | `1e-3` |
| `DT_m` | Transmitter aperture diameter | m | `0.05` |
| `DR_m` | Receiver aperture diameter | m | `0.1` |
| `fov_rad` | Receiver field-of-view half-angle | rad | `π/2` |
| `sens_dbm` | Receiver sensitivity metadata | dBm | `-30.0` |

The transmitter is positioned at the origin and the receiver is positioned along the positive z-axis at the specified `distance_m`.

Additional keyword arguments are retained as environment parameters and are made available to the selected channel models.

---

## 5. ConfiguredChannel API

After calling `build()`, OWCM returns a `ConfiguredChannel`.

### `gain(rng=None)`

Returns the deterministic, mean, or instantaneous dimensionless channel gain produced by the selected composite model.

```python
h = ch.gain()
```

For stochastic models, `gain()` generally represents the deterministic or mean channel contribution implemented by the corresponding model.

**Optional parameter**

- `rng`: random-number generator or integer seed.

---

### `sample(n, rng=None)`

Generates `n` channel-gain samples.

```python
samples = ch.sample(100000, rng=42)
```

**Parameters**

- `n` (`int`): number of samples.
- `rng`: optional integer seed or NumPy random generator.

**Returns**

- NumPy array of dimensionless channel-gain samples.

Providing an integer seed allows stochastic experiments to be reproduced.

---

### `received_power(rng=None)`

Calculates received optical power according to

\[
P_r=P_t h,
\]

where \(h\) is the composite channel gain.

```python
pr = ch.received_power()
```

**Returns**

- Received power in watts.

---

### `received_power_samples(n, rng=None)`

Generates received-power samples.

```python
pr_samples = ch.received_power_samples(10000, rng=42)
```

**Returns**

- NumPy array containing received power in watts.

---

### `outage(threshold_w, n=100000, rng=None)`

Estimates the outage probability

\[
P_{\mathrm{out}}=\Pr(P_r<P_{\mathrm{th}}).
\]

```python
p_out = ch.outage(
    threshold_w=1e-6,
    n=100000,
    rng=42,
)
```

**Parameters**

- `threshold_w` (`float`): received-power threshold in watts.
- `n` (`int`): Monte Carlo sample count; default `100000`.
- `rng`: optional integer seed or NumPy random generator.

**Returns**

- Estimated outage probability between 0 and 1.

---

### `describe()`

Returns a dictionary describing the configured environment, link, and component models.

```python
info = ch.describe()
print(info)
```

---

## 6. Composite-Channel Convention

OWCM represents a channel as a composition of individual propagation factors. For a channel containing \(N\) multiplicative components,

\[
h_{\mathrm{total}}
=
\prod_{i=1}^{N} h_i.
\]

The composite sampling implementation similarly multiplies samples from the selected channel components.

This formulation assumes that the selected multiplicative mechanisms can be represented separately. For stochastic components, the present composite implementation samples each selected component independently unless dependence is explicitly incorporated within an individual model.

Models whose physical contributions are additive, such as the combined indoor LoS and diffuse NLoS implementation, perform that addition internally before entering the composite channel.

---

# 7. Atmospheric Channel API

## 7.1 Atmospheric Recipes

### `mvp`

```text
geometry    = uniform_aperture
attenuation = kim
turbulence  = gamma_gamma
pointing    = rayleigh_gaussian
```

Example:

```python
ch = Channel.environment("atmospheric").defaults("mvp").build(
    distance_m=1000.0,
    wavelength_nm=1550.0,
    pt_w=0.5,
    visibility_km=2.0,
    theta_rad=1e-3,
    gg_alpha=3.2,
    gg_beta=2.1,
    jitter_sigma_m=0.01,
    wz_eq_m=0.1,
)
```

### `clear_air`

```text
geometry    = uniform_aperture
attenuation = beer_lambert
turbulence  = lognormal
pointing    = none
```

### `dense_fog`

```text
geometry    = gaussian_collected_approx
attenuation = kim
turbulence  = gamma_gamma
pointing    = rayleigh_gaussian
```

---

## 7.2 Atmospheric Geometry Models

### `uniform_aperture`

Category:

```text
geometry
```

Implements the geometric collection factor

\[
h_{\mathrm{geo}}
=
\left(
\frac{D_R}
{D_T+R\theta}
\right)^2,
\]

limited to a maximum value of unity.

Uses the common parameters:

- `DT_m`
- `DR_m`
- `distance_m`
- `theta_rad`

---

### `gaussian_collected_exact`

Category:

```text
geometry
```

Implements a Gaussian-beam aperture-collection approximation based on

\[
A_0=
\left[
\operatorname{erf}
\left(
\frac{\sqrt{2}a}{w_z}
\right)
\right]^2,
\]

where \(a=D_R/2\).

Uses:

- `DT_m`
- `DR_m`
- `distance_m`
- `theta_rad`

---

### `gaussian_collected_approx`

Category:

```text
geometry
```

Implements

\[
A_0
=
1-\exp\left(-\frac{2a^2}{w_z^2}\right).
\]

Uses:

- `DT_m`
- `DR_m`
- `distance_m`
- `theta_rad`

---

## 7.3 Atmospheric Attenuation Models

### `beer_lambert`

Category:

```text
attenuation
```

Implements

\[
h_{\mathrm{att}}
=
\exp(-\alpha R).
\]

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `alpha` | Extinction/attenuation coefficient | m\(^{-1}\) | `0.0` |

Example:

```python
ch = (
    Channel.environment("atmospheric")
    .defaults("clear_air")
    .build(
        distance_m=1000.0,
        alpha=1e-4,
    )
)
```

---

### `kim`

Category:

```text
attenuation
```

Visibility-based Kim fog attenuation model.

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `visibility_km` | Meteorological visibility | km | `2.0` |
| `wavelength_nm` | Optical wavelength | nm | `1550.0` |

---

### `kruse`

Category:

```text
attenuation
```

Visibility-based Kruse fog attenuation model.

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `visibility_km` | Meteorological visibility | km | `2.0` |
| `wavelength_nm` | Optical wavelength | nm | `1550.0` |

Example:

```python
ch = (
    Channel.environment("atmospheric")
    .defaults("mvp")
    .model("attenuation", "kruse")
    .build(
        distance_m=1000.0,
        wavelength_nm=1550.0,
        visibility_km=2.0,
    )
)
```

---

### `al_naboulsi_convection`

Category:

```text
attenuation
```

Implements the convection-fog attenuation relation

\[
A
=
4.343
\frac{0.11478\lambda+3.8367}{V},
\]

with wavelength in micrometers and visibility in kilometers.

Required user parameters:

| Parameter | Meaning | Unit |
|---|---|---:|
| `visibility_km` | Visibility | km |
| `wavelength_nm` or `wavelength_um` | Wavelength | nm or µm |

---

### `al_naboulsi_advection`

Category:

```text
attenuation
```

Implements

\[
A
=
4.343
\frac{0.18126\lambda^2+0.13709\lambda+3.7502}{V}.
\]

Required user parameters:

- `visibility_km`
- `wavelength_nm` or `wavelength_um`

---

### `ijaz`

Category:

```text
attenuation
```

Implements the controlled-fog attenuation model

\[
A
=
\frac{17}{V}
\left(\frac{\lambda}{0.55}\right)^{-q(\lambda)},
\]

where

\[
q(\lambda)=0.1428\lambda-0.0947.
\]

Required user parameters:

- `visibility_km`
- `wavelength_nm` or `wavelength_um`

---

### `esmail`

Category:

```text
attenuation
```

Implements the regression form

\[
A=kV^{-(a\lambda+b)}.
\]

The regression coefficients are not internally assumed and must be supplied by the user.

Required parameters:

| Parameter | Meaning |
|---|---|
| `visibility_km` | Visibility in km |
| `wavelength_nm` or `wavelength_um` | Wavelength |
| `k` | Regression coefficient |
| `a` | Regression coefficient |
| `b` | Regression coefficient |

---

## 7.4 Atmospheric Turbulence Models

### `lognormal`

Category:

```text
turbulence
```

Implements unit-mean log-normal turbulence sampling.

| Parameter | Meaning | Default |
|---|---|---:|
| `sigma_R2` | Log-irradiance variance parameter | `0.1` |

`gain()` returns unity, while `sample()` generates stochastic log-normal channel realizations.

Example:

```python
samples = (
    Channel.environment("atmospheric")
    .defaults("clear_air")
    .build(sigma_R2=0.1)
    .sample(100000, rng=42)
)
```

---

### `gamma_gamma`

Category:

```text
turbulence
```

Generates Gamma–Gamma turbulence samples as the product of two independent unit-mean Gamma random variables.

| Parameter | Meaning | Default |
|---|---|---:|
| `gg_alpha` | Gamma–Gamma \(\alpha\) parameter | `2.0` |
| `gg_beta` | Gamma–Gamma \(\beta\) parameter | `2.0` |

`gain()` returns unity and stochastic fading is generated through `sample()`.

---

### `negative_exponential`

Category:

```text
turbulence
```

This model identifier is currently registered, but stochastic sampling is not implemented in the present reference implementation.

---

## 7.5 Atmospheric Pointing Models

### `rayleigh_gaussian`

Category:

```text
pointing
```

Models Rayleigh-distributed radial pointing displacement with Gaussian coupling loss.

\[
h_p
=
\exp\left(
-\frac{2r^2}{w_{\mathrm{eq}}^2}
\right).
\]

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `jitter_sigma_m` | Rayleigh displacement scale | m | `0.01` |
| `wz_eq_m` | Equivalent beam radius | m | `0.1` |

---

### `none`

No pointing loss:

\[
h_p=1.
\]

---

### `hoyt_gaussian`

Registered model identifier. The current implementation raises `NotImplementedError`.

### `beckmann_gaussian`

Registered model identifier. The current implementation raises `NotImplementedError`.

---

# 8. Indoor Channel API

## 8.1 Indoor Recipes

### `los`

```text
los      = lambertian_los
nlos     = none
blockage = none
```

Example:

```python
ch = Channel.environment("indoor").defaults("los").build(
    distance_m=3.0,
    lambertian_order=1.0,
    DR_m=0.01,
    fov_rad=1.0472,
)
```

### `room_mvp`

```text
los      = lambertian_los_plus_nlos
nlos     = none
blockage = onoff
```

### `room_full`

```text
los      = lambertian_los_plus_nlos
nlos     = none
blockage = markov
```

---

## 8.2 Indoor LoS Models

### `lambertian_los`

Category:

```text
los
```

Implements a Lambertian indoor optical LoS channel including receiver aperture, irradiance/incidence angles, optical filtering, concentrator gain, and receiver FOV.

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `lambertian_order` | Lambertian emission order | — | `1.0` if not otherwise specified |
| `semi_angle_half_power_rad` | LED half-power semi-angle used to calculate Lambertian order | rad | optional |
| `concentrator_refractive_index` | Optical concentrator refractive index | — | `1.0` |
| `optical_filter_gain` | Optical filter gain | — | `1.0` |
| `cos_phi` / `cos_irradiance` | Cosine of irradiance angle | — | aligned geometry |
| `cos_psi` / `cos_incidence` | Cosine of incidence angle | — | aligned geometry |

The common `fov_rad` parameter specifies the receiver FOV half-angle.

If explicit orientation cosines are not provided, the current implementation assumes aligned transmitter and receiver orientations.

---

### `lambertian_los_plus_nlos`

Category:

```text
los
```

Computes an additive indoor channel:

\[
H=H_{\mathrm{LoS}}+H_{\mathrm{NLoS}}.
\]

The LoS component uses `lambertian_los`, while the diffuse NLoS component uses the K-bounce model internally.

---

## 8.3 Indoor NLoS Models

### `kbounce`

Category:

```text
nlos
```

Diffuse reflected-path approximation supporting a configurable number of reflection orders.

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `reflectance` or `rho` | Surface reflectance | — | `0.7` |
| `room_area_m2` | Effective room area | m² | `25.0` |
| `n_bounces` or `K` | Number of reflection orders | — | `1` |
| `lambertian_order` | Lambertian order | — | `1.0` |
| `concentrator_refractive_index` | Concentrator refractive index | — | `1.0` |
| `optical_filter_gain` | Optical filter gain | — | `1.0` |
| `ceiling_height_m` | Effective reflector/ceiling height | m | derived from room area |

---

### `none`

No additional NLoS loss factor.

---

## 8.4 Indoor Blockage Models

### `onoff`

Binary independent blockage model.

| Parameter | Meaning | Default |
|---|---|---:|
| `p_blocked` | Probability that the link is blocked | `0.1` |

`gain()` returns

\[
1-p_{\mathrm{blocked}},
\]

while `sample()` generates binary blocked/unblocked realizations.

---

### `markov`

Two-state Markov blockage model.

| Parameter | Meaning | Default |
|---|---|---:|
| `p_01` | Probability of transition from unblocked to blocked | `0.1` |
| `p_10` | Probability of transition from blocked to unblocked | `0.3` |

The steady-state unblocked probability is

\[
P_{\mathrm{unblocked}}
=
\frac{p_{10}}{p_{01}+p_{10}}.
\]

---

### `none`

No blockage loss.

---

# 9. Underwater Channel API

## 9.1 Underwater Recipes

### `beer_lambert`

```text
extinction = a_plus_b
scattering = none
pointing   = none
```

Example:

```python
ch = Channel.environment("underwater").defaults("beer_lambert").build(
    distance_m=10.0,
    attenuation_c=0.1,
)
```

### `los_link`

Uses the analytical underwater LoS link model:

```text
link = los_case
```

### `retro_link`

Uses the modulating-retroreflector link model:

```text
link = retroreflective_case
```

### `reflective_link`

Uses the reflective NLoS model:

```text
nlos = reflective_case
```

---

## 9.2 Underwater Extinction Models

### `a_plus_b`

Category:

```text
extinction
```

Implements Beer–Lambert extinction:

\[
h
=
\exp(-cR).
\]

The extinction coefficient is selected in the following order:

1. `attenuation_c`, when supplied;
2. `attenuation_a + attenuation_b`, when both are supplied;
3. default \(c=0.05~\mathrm{m}^{-1}\).

Parameters:

| Parameter | Meaning | Unit |
|---|---|---:|
| `attenuation_c` | Total extinction coefficient | m\(^{-1}\) |
| `attenuation_a` | Absorption coefficient | m\(^{-1}\) |
| `attenuation_b` | Scattering coefficient | m\(^{-1}\) |

---

### `c_direct`

Direct extinction-coefficient interface. The current implementation follows the same extinction calculation described above.

---

## 9.3 Underwater LoS Link

### `los_case`

Category:

```text
link
```

Implements the Table-XI LoS analytical link formulation included in OWCM.

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `theta_rad` | Off-axis angle | rad | `0.0` |
| `theta0_rad` | Transmitter beam half-angle parameter | rad | `0.174` |
| `etaT` | Transmitter efficiency | — | `0.9` |
| `etaR` | Receiver efficiency | — | `0.9` |
| `attenuation_c` | Water extinction coefficient | m\(^{-1}\) | `0.05` |

Receiver area is calculated from `DR_m`.

Example:

```python
ch = Channel.environment("underwater").defaults("los_link").build(
    distance_m=20.0,
    DR_m=0.1,
    attenuation_c=0.1,
    theta_rad=0.0,
    theta0_rad=0.174,
)
```

---

## 9.4 Underwater Retroreflective Link

### `retroreflective_case`

Category:

```text
link
```

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `theta_rad` | Off-axis angle | rad | `0.0` |
| `theta0_rad` | Forward beam half-angle parameter | rad | `0.174` |
| `theta0_retro_rad` | Retroreflected beam angle parameter | rad | `0.01` |
| `etaT` | Transmitter efficiency | — | `0.9` |
| `etaR` | Receiver efficiency | — | `0.9` |
| `etaRetro` | Retroreflector efficiency | — | `0.9` |
| `ARetro_m2` | Retroreflector area | m² | `0.01` |
| `attenuation_c` | Water extinction coefficient | m\(^{-1}\) | `0.05` |

---

## 9.5 Underwater Reflective NLoS Link

### `reflective_case`

Category:

```text
nlos
```

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `h_m` | Geometric vertical-distance parameter | m | `10.0` |
| `x_m` | Geometric horizontal-distance parameter | m | `10.0` |
| `phi_rad` | Angular variable used by the reflective geometry | rad | `0.0` |
| `theta_min_rad` | Minimum angular limit | rad | `0.0` |
| `theta_max_rad` | Maximum angular limit | rad | `π/4` |
| `n1` | Refractive index of medium 1 | — | `1.33` |
| `n2` | Refractive index of medium 2 | — | `1.0` |
| `etaT` | Transmitter efficiency | — | `0.9` |
| `etaR` | Receiver efficiency | — | `0.9` |
| `attenuation_c` | Water extinction coefficient | m\(^{-1}\) | `0.05` |

---

## 9.6 Underwater Scattering and Pointing

### Scattering `none`

No separate scattering factor is applied.

### Pointing `none`

No pointing loss is applied.

### Pointing `gaussian`

The identifier is registered, but the current Gaussian underwater pointing implementation is not yet available and raises `NotImplementedError`.

---

# 10. Underground Channel API

## 10.1 Underground Recipe

### `mine_mvp`

```text
los       = lambertian_los
dust      = exp_extinction
blockage  = markov
multipath = none
```

Example:

```python
ch = Channel.environment("underground").defaults("mine_mvp").build(
    distance_m=20.0,
    dust_conc_mg_m3=0.01,
    p_01=0.1,
    p_10=0.3,
)
```

---

## 10.2 Underground LoS Model

### `lambertian_los`

Category:

```text
los
```

The currently registered implementation uses a simplified distance-dependent LoS factor approximately proportional to

\[
h_{\mathrm{LoS}}
\propto
\frac{1}{R^2}.
\]

This model is intended as a simplified baseline rather than a complete tunnel optical-propagation solution.

---

## 10.3 Dust Model

### `exp_extinction`

Category:

```text
dust
```

The current implementation applies exponential attenuation based on dust concentration.

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `dust_conc_mg_m3` | Dust mass concentration | mg/m³ | `0.0` |

The current registered implementation uses an internal specific-extinction coefficient of `0.5`; this coefficient should be treated as a model parameter requiring application-specific calibration.

---

### `none`

No dust attenuation.

---

## 10.4 Underground Blockage

### `onoff`

| Parameter | Meaning | Default |
|---|---|---:|
| `p_blocked` | Independent blockage probability | `0.1` |

### `markov`

| Parameter | Meaning | Default |
|---|---|---:|
| `p_01` | Unblocked-to-blocked transition probability | `0.1` |
| `p_10` | Blocked-to-unblocked transition probability | `0.3` |

### `none`

No blockage.

---

## 10.5 Underground Multipath

### `none`

No multipath correction.

### `kbounce`

The identifier is currently registered as a placeholder and presently behaves as a unity multiplier. Detailed tunnel-wall K-bounce propagation is not yet implemented.

---

# 11. Space Channel API

## 11.1 Space Recipe

### `deep_space`

```text
free_space       = fspl
tx_gain          = diffraction_limited
rx_gain          = telescope
pointing         = none
atmospheric_entry = none
link_budget      = multiplicative_chain
```

Example:

```python
ch = Channel.environment("space").defaults("deep_space").build(
    distance_m=1.0e9,
    wavelength_nm=1550.0,
    pt_w=1.0,
    DR_m=0.5,
)
```

---

## 11.2 Free-Space Propagation

### `fspl`

Category:

```text
free_space
```

Implements

\[
h_{\mathrm{fs}}
=
\left(
\frac{\lambda}{4\pi R}
\right)^2.
\]

Uses:

- `distance_m`
- `wavelength_nm`

---

## 11.3 Deep-Space Table Model

### `table_xiii`

Category:

```text
deepspace
```

This is a standalone deep-space analytical model that combines free-space loss, transmitter gain, receiver gain, pointing loss, additional link-loss factors, and terminal efficiencies.

Because this model already contains the complete multiplicative chain internally, it should normally be selected as a standalone model rather than multiplied by the `deep_space` recipe.

Example:

```python
ch = (
    Channel.environment("space")
    .model("deepspace", "table_xiii")
    .build(
        distance_m=1.0e9,
        wavelength_nm=1550.0,
        DR_m=0.5,
        w0_rad=1e-5,
        sigma_p=1e-6,
        gamma_r=0.0,
        La=1.0,
        Ls=1.0,
        Lb=1.0,
        eta_t=0.9,
        eta_r=0.9,
    )
)
```

Parameters:

| Parameter | Meaning | Unit | Default |
|---|---|---:|---:|
| `w0_rad` | Beam-divergence parameter used in transmitter gain | rad | required |
| `gamma_r` | Receiver obscuration/geometry parameter | — | `0.0` |
| `sigma_p` | Pointing-error scale | rad | `0.0` |
| `p0` | Pointing-loss coefficient | — | `1.0` |
| `La` | Atmospheric/additional loss factor | — | `1.0` |
| `Ls` | Additional propagation loss factor | — | `1.0` |
| `Lb` | Additional link-loss factor | — | `1.0` |
| `eta_t` | Transmitter efficiency | — | `0.9` |
| `eta_r` | Receiver efficiency | — | `0.9` |

The model implements

\[
L_{\mathrm{fs}}
=
\left(
\frac{\lambda}{4\pi R}
\right)^2,
\]

\[
G_t
=
\frac{8}{w_0^2},
\]

and

\[
G_r
=
\left(
\frac{\pi D_R}{\lambda}
\right)^2
(1-\gamma_r^2).
\]

The total dimensionless gain is calculated internally from the selected link factors.

---

## 11.4 Other Space Components

### `diffraction_limited`

Category:

```text
tx_gain
```

The current implementation is registered but presently returns a unity factor. It should therefore be regarded as a placeholder component in the current release.

### `telescope`

Category:

```text
rx_gain
```

The current implementation is registered but presently returns a unity factor.

### Pointing `none`

Returns unity.

### Pointing `gaussian`

Registered but not implemented; calling this model raises `NotImplementedError`.

### Atmospheric entry `none`

Returns unity and is appropriate when no atmospheric propagation segment is included.

### Atmospheric entry `beer_lambert`

Registered but not implemented in the current release.

### `multiplicative_chain`

Identity factor used because multiplication of the selected space-channel components is already performed by `CompositeChannel`.

---

# 12. Random-Number Control

OWCM accepts either an integer seed or a NumPy random generator for stochastic channel operations.

Example using a fixed seed:

```python
samples_1 = ch.sample(10000, rng=42)
samples_2 = ch.sample(10000, rng=42)
```

Using the same model configuration and seed is intended to provide reproducible random sampling.

A NumPy generator may also be supplied:

```python
import numpy as np

rng = np.random.default_rng(42)
samples = ch.sample(10000, rng=rng)
```

---

# 13. Model Inspection

The configured model stack can be inspected using:

```python
print(ch.describe())
```

Example structure:

```python
{
    "environment": "atmospheric",
    "link": {
        "range_m": 1000.0,
        "wavelength_nm": 1550.0
    },
    "model": {
        "type": "CompositeChannel",
        "components": [...]
    }
}
```

Available model identifiers can be queried without manually inspecting the source code:

```python
builder = Channel.environment("atmospheric")
print(builder.list_models())
```

---

# 14. Implementation Status and Scope

OWCM is intended as a reproducible reference implementation of representative optical wireless channel models discussed in the associated survey. The API distinguishes between fully implemented models and identifiers reserved for models that are still incomplete.

The following registered components have known implementation limitations in the current release:

| Environment | Model | Current status |
|---|---|---|
| Atmospheric | `negative_exponential` | stochastic sampling not implemented |
| Atmospheric | `hoyt_gaussian` | not implemented |
| Atmospheric | `beckmann_gaussian` | not implemented |
| Underwater | pointing `gaussian` | not implemented |
| Underground | multipath `kbounce` | placeholder unity factor |
| Space | `diffraction_limited` | placeholder unity factor |
| Space | `telescope` | placeholder unity factor |
| Space | pointing `gaussian` | not implemented |
| Space | atmospheric-entry `beer_lambert` | not implemented |

These limitations are documented so that registered model identifiers are not interpreted as evidence of complete physical implementation.

---

# 15. Units Convention

Unless explicitly stated otherwise, OWCM uses the following conventions:

| Quantity | Unit |
|---|---|
| Distance | m |
| Aperture diameter | m |
| Wavelength | nm |
| Angular quantities | rad |
| Optical power | W or dBm as indicated |
| Visibility | km |
| Atmospheric extinction coefficient | m\(^{-1}\) |
| Underwater extinction/absorption/scattering coefficient | m\(^{-1}\) |
| Dust concentration | mg/m³ |
| Channel gain | dimensionless |
| Outage probability | dimensionless |

Users should verify that parameters obtained from external literature are converted to these units before supplying them to OWCM.

---

# 16. Minimal Examples

## Atmospheric

```python
from owcm import Channel

ch = Channel.environment("atmospheric").defaults("mvp").build(
    distance_m=1000.0,
    wavelength_nm=1550.0,
    pt_w=0.5,
    visibility_km=2.0,
    theta_rad=1e-3,
    gg_alpha=3.2,
    gg_beta=2.1,
)

print(ch.gain())
print(ch.received_power())
print(ch.outage(1e-6, n=100000, rng=42))
```

## Indoor

```python
ch = Channel.environment("indoor").defaults("los").build(
    distance_m=3.0,
    wavelength_nm=850.0,
    DR_m=0.01,
    lambertian_order=1.0,
)

print(ch.gain())
```

## Underwater

```python
ch = Channel.environment("underwater").defaults("beer_lambert").build(
    distance_m=10.0,
    wavelength_nm=520.0,
    attenuation_c=0.1,
)

print(ch.gain())
```

## Underground

```python
ch = Channel.environment("underground").defaults("mine_mvp").build(
    distance_m=20.0,
    wavelength_nm=850.0,
    dust_conc_mg_m3=0.01,
    p_01=0.1,
    p_10=0.3,
)

print(ch.gain())
```

## Space

```python
ch = Channel.environment("space").defaults("deep_space").build(
    distance_m=1e9,
    wavelength_nm=1550.0,
    pt_w=1.0,
)

print(ch.gain())
```

---

## 17. Reproducibility

For results intended to be reproduced exactly:

1. use the dependency versions listed in `requirements-reproducibility.txt`;
2. report all non-default model parameters;
3. use a fixed random seed for stochastic simulations;
4. record the OWCM release/tag used for the experiment; and
5. retain the scripts used to generate reported figures and tables.

Example:

```python
samples = ch.sample(
    n=100000,
    rng=42,
)
```

The software release, parameter provenance, numerical-validation tolerances, and paper-reproduction scripts are documented separately in the OWCM repository.
