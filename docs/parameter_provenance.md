# OWCM Parameter and Model Provenance

This document records the provenance of the analytical expressions, model parameters, numerical defaults, and implementation assumptions used in the Optical Wireless Communication Channel Model (OWCM) library.

The purpose of this document is to distinguish parameters derived from published literature from values introduced only as software defaults or illustrative simulation settings. A default value provided by OWCM should not be interpreted as a universally recommended physical value unless a literature source is explicitly identified.

## Provenance Categories

OWCM uses the following provenance classifications:

- **Literature-derived:** Equation or parameter obtained directly from a cited publication.
- **Survey-derived:** Equation reproduced from or mapped to the accompanying OWC survey manuscript.
- **User-supplied:** No fixed numerical value is assumed; the user must provide the parameter.
- **Implementation default:** Numerical value introduced to allow immediate execution of the software. It is not claimed to represent a universal physical value.
- **Illustrative scenario:** Value selected for demonstration, plotting, or example simulations.
- **Placeholder:** Component registered in the software architecture but not yet implemented as a validated physical model.

Reference numbers below correspond to the bibliography of the accompanying survey manuscript.

---

# 1. Common Link Parameters

The following parameters are created by the common OWCM channel builder when the user does not provide explicit values.

| Parameter | Default | Unit | Provenance | Interpretation |
|---|---:|---|---|---|
| `distance_m` | 1000 | m | Implementation default | Generic Tx–Rx distance |
| `wavelength_nm` | 1550 | nm | Implementation default | Common FSO wavelength; not required by all environments |
| `pt_dbm` | 0 | dBm | Implementation default | Generic transmit-power value |
| `theta_rad` | \(10^{-3}\) | rad | Implementation default | Generic beam-divergence value |
| `DT_m` | 0.05 | m | Implementation default | Generic transmitter aperture diameter |
| `DR_m` | 0.10 | m | Implementation default | Generic receiver aperture diameter |
| `fov_rad` | \(\pi/2\) | rad | Implementation default | Receiver field-of-view half-angle |
| `sens_dbm` | -30 | dBm | Implementation default | Receiver-sensitivity metadata |

These defaults are provided for software usability and are not intended to define standardized OWC hardware configurations.

---

# 2. Atmospheric Channel Models

## 2.1 Beer–Lambert Attenuation

Model identifier:

```text
atmospheric / attenuation / beer_lambert
```

Implemented relation:

\[
h_{\mathrm{att}}=\exp(-\alpha R).
\]

**Provenance:** Classical Beer–Lambert attenuation law and the common attenuation framework described in the survey.

| Parameter | Default | Provenance |
|---|---:|---|
| `alpha` | 0.0 m\(^{-1}\) | Implementation default |
| \(R\) | User/link supplied | Link geometry |

The value `alpha = 0` corresponds to no attenuation and is provided as a neutral software default. A physically meaningful simulation should supply an environment-appropriate attenuation coefficient.

---

## 2.2 Kim Fog Model

Model identifier:

```text
atmospheric / attenuation / kim
```

Implemented relation:

\[
\alpha_{\mathrm{fog}}
=
\frac{3.91}{V}
\left(
\frac{\lambda}{550}
\right)^{-q(V)},
\]

with the visibility-dependent Kim exponent \(q(V)\).

**Provenance:** Kim visibility model, cited as Ref. [32] in the survey and summarized in the atmospheric empirical-model section.

| Parameter | Default | Unit | Provenance |
|---|---:|---|---|
| `visibility_km` | 2.0 | km | Implementation/example default |
| `wavelength_nm` | Common link value | nm | User/link supplied |
| \(q(V)\) | Piecewise relation | — | Literature-derived |

The default visibility of 2 km is an OWCM example value and should not be interpreted as a standard atmospheric condition.

---

## 2.3 Kruse Fog Model

Model identifier:

```text
atmospheric / attenuation / kruse
```

Implemented relation:

\[
\alpha_{\mathrm{fog}}
=
\frac{3.91}{V}
\left(
\frac{\lambda}{550}
\right)^{-q(V)}.
\]

The Kruse visibility exponent is evaluated using the corresponding visibility-dependent formulation.

**Provenance:** Kruse et al., Ref. [5] of the survey.

| Parameter | Default | Unit | Provenance |
|---|---:|---|---|
| `visibility_km` | 2.0 | km | Implementation/example default |
| `wavelength_nm` | Common link value | nm | User/link supplied |
| \(q(V)\) | Kruse relation | — | Literature-derived |

---

## 2.4 Al Naboulsi Convection Fog Model

Model identifier:

```text
atmospheric / attenuation / al_naboulsi_convection
```

Implemented attenuation:

\[
A
=
4.343
\frac{0.11478\lambda+3.8367}{V},
\]

where \(A\) is in dB/km, \(\lambda\) is in \(\mu\)m, and \(V\) is in km.

**Provenance:** Al Naboulsi et al., Ref. [6] of the survey.

| Parameter | Source |
|---|---|
| Numerical coefficients | Literature-derived |
| `visibility_km` | User supplied |
| Wavelength | User/link supplied |

No fixed visibility value is imposed by this model.

---

## 2.5 Al Naboulsi Advection Fog Model

Model identifier:

```text
atmospheric / attenuation / al_naboulsi_advection
```

Implemented attenuation:

\[
A
=
4.343
\frac{0.18126\lambda^2+0.13709\lambda+3.7502}{V}.
\]

**Provenance:** Al Naboulsi et al., Ref. [6] of the survey.

The polynomial coefficients are literature-derived. Visibility and wavelength are supplied by the user or link configuration.

---

## 2.6 Ijaz Controlled-Fog Model

Model identifier:

```text
atmospheric / attenuation / ijaz
```

Implemented relation:

\[
A
=
\frac{17}{V}
\left(
\frac{\lambda}{0.55}
\right)^{-q(\lambda)},
\]

where

\[
q(\lambda)=0.1428\lambda-0.0947.
\]

**Provenance:** Ijaz et al., Ref. [51] of the survey.

The numerical coefficients are literature-derived. Visibility and wavelength are supplied by the simulation configuration.

---

## 2.7 Esmail Regression Model

Model identifier:

```text
atmospheric / attenuation / esmail
```

Implemented structure:

\[
A=kV^{-(a\lambda+b)}.
\]

**Provenance:** Esmail et al., Ref. [52] of the survey.

The library does **not** assume numerical values for \(k\), \(a\), and \(b\). These coefficients must be supplied by the user because they depend on the fitted regression dataset.

| Parameter | Provenance |
|---|---|
| `k` | User supplied from selected Esmail regression fit |
| `a` | User supplied from selected Esmail regression fit |
| `b` | User supplied from selected Esmail regression fit |
| `visibility_km` | User supplied |
| wavelength | User/link supplied |

---

# 3. Atmospheric Turbulence Models

## 3.1 Log-Normal Turbulence

Model identifier:

```text
atmospheric / turbulence / lognormal
```

The log-normal distribution is used for weak-turbulence irradiance fluctuations.

**Provenance:** Standard optical-turbulence formulation summarized in the survey, including Ref. [10].

The implementation generates unit-mean samples by choosing

\[
\mu=-\frac{\sigma^2}{2}.
\]

| Parameter | Default | Provenance |
|---|---:|---|
| `sigma_R2` | 0.1 | Implementation/example default |

The default value 0.1 is an illustrative software setting and should be replaced by a turbulence parameter appropriate to the physical link.

---

## 3.2 Gamma–Gamma Turbulence

Model identifier:

```text
atmospheric / turbulence / gamma_gamma
```

The Gamma–Gamma channel is generated as the product of two independent unit-mean Gamma random variables representing large- and small-scale irradiance fluctuations.

**Provenance:** Gamma–Gamma formulation summarized in the survey and standard optical-turbulence literature, including Refs. [10] and [44].

| Parameter | Default | Provenance |
|---|---:|---|
| `gg_alpha` | 2.0 | Implementation/example default |
| `gg_beta` | 2.0 | Implementation/example default |

The values \(\alpha=\beta=2\) are not claimed as universal turbulence parameters. For physically defined links, \(\alpha\) and \(\beta\) should be calculated or selected according to the turbulence regime.

---

## 3.3 Negative-Exponential Turbulence

Model identifier:

```text
atmospheric / turbulence / negative_exponential
```

**Provenance:** Standard saturated-turbulence statistical model.

**Implementation status:** Placeholder. Stochastic sampling is not implemented in the current OWCM release.

---

# 4. Atmospheric Pointing Model

## Rayleigh–Gaussian Pointing Error

Model identifier:

```text
atmospheric / pointing / rayleigh_gaussian
```

Implemented instantaneous pointing loss:

\[
h_{\mathrm{pe}}
=
\exp
\left(
-\frac{2r^2}{w_{\mathrm{eq}}^2}
\right),
\]

where radial displacement \(r\) follows a Rayleigh distribution for independent zero-mean Gaussian displacement components.

**Provenance:** Gaussian pointing-loss formulation and Rayleigh radial-displacement model summarized in the survey pointing-error section, including Ref. [27].

| Parameter | Default | Unit | Provenance |
|---|---:|---|---|
| `jitter_sigma_m` | 0.01 | m | Implementation/example default |
| `wz_eq_m` | 0.10 | m | Implementation/example default |

These values are intended only to provide executable defaults.

The registered Hoyt and Beckmann pointing models are currently placeholders and are not considered validated implementations.

---

# 5. Atmospheric Geometric Models

## Uniform-Aperture Approximation

Model identifier:

```text
atmospheric / geometry / uniform_aperture
```

Implemented relation:

\[
h_{\mathrm{geo}}
=
\left(
\frac{D_R}
{D_T+R\theta}
\right)^2.
\]

**Provenance:** Survey-level geometric link approximation.

The implementation limits the resulting gain to unity.

The aperture diameters, link range, and divergence angle are obtained from the common link configuration.

---

## Gaussian Aperture Collection

Model identifiers:

```text
gaussian_collected_exact
gaussian_collected_approx
```

The implemented aperture-coupling expressions follow Gaussian-beam collection approximations described in the survey framework.

The current software approximates the receiver-plane beam radius from transmitter aperture, range, and divergence. Therefore, these models should be interpreted as reduced-order engineering approximations rather than full Gaussian-beam propagation solvers.

---

# 6. Indoor Optical Channel Models

## 6.1 Lambertian LoS Model

Model identifier:

```text
indoor / los / lambertian_los
```

The implementation follows the standard Lambertian indoor OWC formulation, including:

\[
m
=
-\frac{\ln 2}
{\ln(\cos\phi_{1/2})},
\]

Lambertian radiant intensity,

\[
R_o(\phi)
=
\frac{m+1}{2\pi}
\cos^m(\phi),
\]

optical concentrator gain, and LoS DC channel gain.

**Provenance:** Indoor OWC equations summarized in the survey, currently Eqs. (40)–(44), based on Refs. [68]–[72].

| Parameter | Default | Provenance |
|---|---:|---|
| `lambertian_order` | 1.0 | Implementation default when semi-angle is not supplied |
| `concentrator_refractive_index` | 1.0 | Neutral implementation default |
| `optical_filter_gain` | 1.0 | Neutral implementation default |
| Irradiance/incidence orientation | Aligned | Simplifying implementation assumption |

When a half-power semi-angle is supplied, the Lambertian order is calculated rather than using the default value.

---

## 6.2 Indoor Diffuse/K-Bounce Model

Model identifier:

```text
indoor / nlos / kbounce
```

**Provenance:** Recursive/diffuse reflection framework summarized in the survey, currently Eqs. (45)–(53), including Refs. [73]–[76].

The current OWCM implementation is a reduced-order approximation and does not perform full surface discretization or ray tracing.

| Parameter | Default | Provenance |
|---|---:|---|
| Surface reflectance `rho` | 0.7 | Implementation/example default |
| `room_area_m2` | 25.0 m² | Implementation/example default |
| Number of bounces `K` | 1 | Implementation default |
| Lambertian order | 1.0 | Implementation default |
| Effective ceiling height | \(0.6\sqrt{A_{\rm room}}\) | OWCM approximation |
| Effective reflecting area | \(A_{\rm room}/4\) | OWCM approximation |

These geometric defaults are not claimed as standard room parameters and should be explicitly specified for a physical deployment.

---

# 7. Indoor Blockage Models

## Independent On–Off Blockage

| Parameter | Default | Provenance |
|---|---:|---|
| `p_blocked` | 0.1 | Implementation/example default |

The value is not derived from a universal indoor-blockage measurement dataset.

## Two-State Markov Blockage

| Parameter | Default | Provenance |
|---|---:|---|
| `p_01` | 0.1 | Implementation/example default |
| `p_10` | 0.3 | Implementation/example default |

These transition probabilities are illustrative and should be calibrated from scenario-specific blockage statistics when quantitative predictions are required.

---

# 8. Underwater Channel Models

## 8.1 Extinction Model

Model identifiers:

```text
underwater / extinction / a_plus_b
underwater / extinction / c_direct
```

OWCM uses

\[
c(\lambda)=a(\lambda)+b(\lambda)
\]

and

\[
L_{\mathrm{pr}}(\lambda,R)
=
\exp[-c(\lambda)R].
\]

**Provenance:** Underwater attenuation framework summarized in the survey, including Eq. (7) and the Beer–Lambert underwater propagation expression.

| Parameter | Default | Unit | Provenance |
|---|---:|---|---|
| `attenuation_c` | 0.05 | m\(^{-1}\) | Implementation/example default |
| `attenuation_a` | User supplied | m\(^{-1}\) | Physical input |
| `attenuation_b` | User supplied | m\(^{-1}\) | Physical input |

The value \(c=0.05~\mathrm{m}^{-1}\) is used as an illustrative clear-water setting in OWCM and should not be interpreted as a universal extinction coefficient.

---

## 8.2 Underwater LoS Model

Model identifier:

```text
underwater / link / los_case
```

The implementation follows the survey's analytical underwater LoS received-power model, currently Eq. (55), based on Ref. [14].

| Parameter | Default | Provenance |
|---|---:|---|
| `theta_rad` | 0 | Aligned-link implementation default |
| `theta0_rad` | 0.174 rad | Illustrative value approximately equal to 10° |
| `etaT` | 0.9 | Implementation/example default |
| `etaR` | 0.9 | Implementation/example default |
| `attenuation_c` | 0.05 m\(^{-1}\) | Implementation/example default |

The analytical equation is literature-derived, while the numerical defaults above are OWCM scenario values unless explicitly replaced by user-supplied hardware/environment parameters.

---

## 8.3 Modulating Retroreflector Model

Model identifier:

```text
underwater / link / retroreflective_case
```

**Provenance:** Retroreflector received-power formulation summarized in the survey, currently Eq. (56), based on Ref. [14].

| Parameter | Default | Provenance |
|---|---:|---|
| `theta_rad` | 0 | Implementation default |
| `theta0_rad` | 0.174 rad | Illustrative value |
| `theta0_retro_rad` | 0.01 rad | Illustrative value |
| `etaT` | 0.9 | Implementation/example default |
| `etaR` | 0.9 | Implementation/example default |
| `etaRetro` | 0.9 | Implementation/example default |
| `ARetro_m2` | 0.01 m² | Implementation/example default |
| `attenuation_c` | 0.05 m\(^{-1}\) | Implementation/example default |

---

## 8.4 Reflective Underwater NLoS Model

Model identifier:

```text
underwater / nlos / reflective_case
```

**Provenance:** Reflective water–air-interface model summarized in the survey, currently Eqs. (57)–(58), based on Ref. [14].

| Parameter | Default | Provenance |
|---|---:|---|
| `h_m` | 10 m | Implementation/example default |
| `x_m` | 10 m | Implementation/example default |
| `phi_rad` | 0 | Implementation geometry default |
| `theta_min_rad` | 0 | Implementation default |
| `theta_max_rad` | \(\pi/4\) | Implementation/example default |
| `n1` | 1.33 | Representative water refractive index |
| `n2` | 1.0 | Representative air refractive index |
| `etaT` | 0.9 | Implementation/example default |
| `etaR` | 0.9 | Implementation/example default |

The geometric variables should be supplied according to the simulated physical configuration for quantitative use.

---

# 9. Underground Channel Models

## 9.1 Underground LoS

Model identifier:

```text
underground / los / lambertian_los
```

The current OWCM implementation uses the reduced-order relation

\[
h_{\mathrm{LoS}}\propto \frac{1}{R^2}.
\]

**Provenance:** Motivated by the Lambertian LoS framework discussed for underground optical channels in the survey.

**Implementation classification:** Engineering simplification.

The current implementation does not reproduce the complete angular Lambertian formulation used in the indoor model.

---

## 9.2 Dust Extinction

Model identifier:

```text
underground / dust / exp_extinction
```

Implemented relation:

\[
h_{\mathrm{dust}}
=
\exp(-kCR),
\]

where \(C\) is dust concentration.

| Parameter | Default | Provenance |
|---|---:|---|
| `dust_conc_mg_m3` | 0 | Neutral implementation default |
| `dust_k_per_m_per_mg_m3` | 0.5 | OWCM placeholder/calibration parameter |

The value \(k=0.5\) is **not currently tied to a validated literature source** and must therefore be treated as an illustrative implementation parameter. Quantitative studies should replace it with a calibrated or literature-supported extinction coefficient.

This parameter is specifically flagged for future validation.

---

## 9.3 Underground Blockage

The underground on–off and Markov blockage implementations use the same generic statistical structure as the indoor blockage models.

| Parameter | Default | Provenance |
|---|---:|---|
| `p_blocked` | 0.1 | Implementation/example default |
| `p_01` | 0.1 | Implementation/example default |
| `p_10` | 0.3 | Implementation/example default |

These values require scenario-specific calibration for predictive underground-channel modeling.

---

## 9.4 Underground K-Bounce Multipath

Model identifier:

```text
underground / multipath / kbounce
```

**Implementation status:** Placeholder.

The current registered model returns a unity factor and therefore does not constitute a validated underground multipath implementation.

---

# 10. Space Optical Channel Models

## 10.1 Free-Space Propagation Loss

Model identifier:

```text
space / free_space / fspl
```

Implemented relation:

\[
h_{\mathrm{fs}}
=
\left(
\frac{\lambda}{4\pi R}
\right)^2.
\]

**Provenance:** Friis free-space propagation relation used in the survey's space-channel section, currently Eq. (68), Ref. [123].

Parameters \(R\) and \(\lambda\) are obtained from the link configuration.

---

## 10.2 Deep-Space Analytical Link Model

Model identifier:

```text
space / deepspace / table_xiii
```

The implementation follows the survey deep-space link-budget structure:

\[
P_{\mathrm{Rap}}
=
P_TG_TG_Rh_{\mathrm{fs}}L_aL_sL_b
h_{\mathrm{pe}}\eta_T\eta_R.
\]

The associated transmitter, receiver, free-space, and pointing expressions correspond to the deep-space analytical model summarized in the survey's space section.

Current manuscript mapping:

- Link-budget formulation: Eq. (65), Ref. [118]
- Transmitter aperture gain: Eq. (66), Ref. [119]
- Receiver aperture gain: Eq. (67), Ref. [120]
- Free-space propagation: Eq. (68), Ref. [123]
- Pointing-loss formulation: Eq. (69), Ref. [127]

| Parameter | Default | Provenance |
|---|---:|---|
| `w0_rad` | Required | User supplied |
| `gamma_r` | 0 | Unobscured-receiver default |
| `sigma_p` | 0 | No-pointing-error default |
| `p0` | 1 | Neutral implementation default |
| `La` | 1 | Neutral/no-loss default |
| `Ls` | 1 | Neutral/no-loss default |
| `Lb` | 1 | Neutral/no-loss default |
| `eta_t` | 0.9 | Implementation/example default |
| `eta_r` | 0.9 | Implementation/example default |

Values equal to unity represent neutral loss factors rather than measured physical parameters.

---

## 10.3 Space Components Currently Registered as Placeholders

The following identifiers are part of the OWCM architecture but are not independent validated implementations in the current release:

```text
space / tx_gain / diffraction_limited
space / rx_gain / telescope
space / pointing / gaussian
space / atmospheric_entry / beer_lambert
```

The first two currently return unity when used as individual factors, while the latter two are not fully implemented.

Users requiring the corresponding space-link physics should use the complete implemented analytical model or supply validated component implementations.

---

# 11. Random-Number Provenance and Reproducibility

Stochastic OWCM models use NumPy random-number generation.

For reproducible simulations, the random seed must be recorded explicitly.

Example:

```python
samples = channel.sample(
    n=100000,
    rng=42,
)
```

A random seed is a numerical reproducibility setting and has no physical interpretation.

---

# 12. Interpretation of Default Parameters

OWCM distinguishes between a **model equation** and a **scenario parameter**.

A literature-derived equation does not imply that every numerical default in its software implementation is literature-derived.

For example:

```text
Gamma–Gamma distribution     -> literature-derived model
gg_alpha = 2.0               -> OWCM example default
gg_beta = 2.0                -> OWCM example default
```

Similarly:

```text
Underwater Beer–Lambert law  -> literature-derived model
c = 0.05 m^-1                -> OWCM example/default condition
```

Users should explicitly report parameter values used for published numerical results rather than relying implicitly on package defaults.

---

# 13. Known Provenance Items Requiring Further Validation

The following implementation parameters should not presently be interpreted as literature-validated constants:

- atmospheric default visibility of 2 km;
- log-normal default variance of 0.1;
- Gamma–Gamma defaults \(\alpha=\beta=2\);
- pointing defaults `jitter_sigma_m = 0.01` and `wz_eq_m = 0.1`;
- indoor room area of 25 m²;
- indoor surface reflectance of 0.7;
- indoor blockage probabilities;
- underwater extinction default \(c=0.05~\mathrm{m}^{-1}\);
- underwater terminal efficiencies of 0.9;
- retroreflector default geometry and efficiency parameters;
- underground blockage probabilities;
- underground dust-specific extinction coefficient \(k=0.5\);
- deep-space terminal efficiencies of 0.9.

These parameters are retained as executable or illustrative defaults. Studies requiring quantitatively predictive results should replace them with values obtained from measurements, standards, manufacturer specifications, or cited literature.

---

# 14. Manuscript-to-Code Equation Mapping

The OWCM source code was developed alongside multiple revisions of the survey manuscript. Consequently, some source-code comments may contain equation or table numbers from an earlier manuscript version.

The current manuscript uses, among others:

| Environment | Current manuscript equations |
|---|---|
| Indoor Lambertian/received-power models | Eqs. (40)–(53) |
| Underwater analytical models | Eqs. (54)–(58) |
| Underground models | Eqs. (59)–(64) |
| Space optical models | Eqs. (65)–(70) |

The physical expressions, model names, and literature references should therefore be used as the primary provenance identifiers. Equation numbers in source-code comments should be synchronized with the final accepted manuscript before the permanent OWCM release is tagged.

---

# 15. Citation Policy

For every model added to OWCM, contributors should document:

1. the original publication, standard, or authoritative source;
2. the mathematical expression implemented;
3. units of all parameters;
4. valid physical regime;
5. whether numerical defaults originate from literature or are illustrative;
6. numerical or modeling assumptions introduced by the implementation; and
7. known implementation limitations.

New model implementations should not introduce unexplained numerical constants.
