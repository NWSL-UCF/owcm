# OWCM Registry Documentation

This document lists all standardized Environment IDs, Category IDs, Model IDs, and Recipes available in the `OWCM` library.

## 1. Global Naming Rules

- **Environment IDs**: `atmospheric`, `indoor`, `underwater`, `underground`, `space`
- **Model IDs**: Lowercase `snake_case`, no units.
- **Recipe IDs**: `mvp` (always present), plus environment-specifics.

## 2. Atmospheric (`atmospheric`)

### Categories
- `geometry`, `attenuation`, `turbulence`, `pointing`, `sinr`

### Models

| Category | Model ID | Description |
| :--- | :--- | :--- |
| **geometry** | `uniform_aperture` | Standard geometric loss $(D_R / (D_T + R\theta))^2$ |
| | `gaussian_collected_exact` | $A_0 = [\text{erf}(v)]^2$ |
| | `gaussian_collected_approx` | $A_0 \approx 1 - \exp(-2a^2/w_z^2)$ |
| **attenuation** | `beer_lambert` | $\tau = \exp(-\alpha R)$ |
| | `kim` | Visibility model with low-vis correction |
| | `kruse` | Standard visibility model |
| | `al_naboulsi_convection` | Convection fog polynomial |
| | `al_naboulsi_advection` | Advection fog polynomial |
| | `ijaz` | Controlled fog chamber model |
| | `esmail` | Unified regression model |
| **turbulence** | `lognormal` | Weak turbulence fading |
| | `gamma_gamma` | Weak-to-strong turbulence fading |
| | `negative_exponential` | Saturated turbulence fading |
| | `malaga` | M-distribution (Phase 3) |
| **pointing** | `rayleigh_gaussian` | Rayleigh jitter + Gaussian loss |
| | `hoyt_gaussian` | Hoyt jitter + Gaussian loss |
| | `beckmann_gaussian` | Beckmann jitter + Gaussian loss |
| | `none` | No pointing loss |

### Recipes

- **`mvp`**: `uniform_aperture`, `kim`, `gamma_gamma`, `rayleigh_gaussian`
- **`clear_air`**: `uniform_aperture`, `beer_lambert`, `lognormal`, `none`
- **`dense_fog`**: `gaussian_collected_approx`, `kim`, `gamma_gamma`, `rayleigh_gaussian`

## 3. Indoor (`indoor`)

### Categories
- `los`, `nlos`, `blockage`

### Models

| Category | Model ID | Description |
| :--- | :--- | :--- |
| **los** | `lambertian_los` | DC gain with FOV cutoff |
| **nlos** | `kbounce` | K-bounce reflected path |
| | `none` | No reflected path |
| **blockage** | `onoff` | i.i.d. blockage |
| | `markov` | Bursty Markov blockage |
| | `none` | No blockage |

### Recipes

- **`los`**: `lambertian_los`, `none` (nlos), `none` (blockage)
- **`room_mvp`**: `lambertian_los`, `kbounce`, `onoff`

## 4. Underwater (`underwater`)

### Categories
### Categories
- `extinction`, `scattering`, `pointing`, `nlos`, `link`

### Models

| Category | Model ID | Description |
| :--- | :--- | :--- |
| **extinction** | `a_plus_b` | $c = a + b$ |
| | `c_direct` | User supplies $c$ directly |
| **scattering** | `none` | Ignore extra scattering |
| **pointing** | `none` | No pointing loss |
| | `gaussian` | Gaussian pointing penalty |
| **nlos** | `reflective_case` | Table XI Reflective (Eq 91-92) |
| **link** | `los_case` | Table XI LoS (Eq 89) |
|      | `retroreflective_case` | Table XI Retroreflector (Eq 90) |

### Recipes

- **`beer_lambert`**: `a_plus_b`, `none` (scattering), `none` (pointing)

## 5. Underground (`underground`)

### Categories
- `los`, `dust`, `blockage`, `multipath`

### Models

| Category | Model ID | Description |
| :--- | :--- | :--- |
| **los** | `lambertian_los` | Baseline LoS gain |
| **dust** | `exp_extinction` | $\exp(-\alpha_{dust} R)$ |
| | `none` | No dust |
| **blockage** | `onoff` | i.i.d. blockage |
| | `markov` | Bursty blockage |
| | `none` | No blockage |
| **multipath** | `none` | No multipath |
| | `kbounce` | K-bounce reflections |

### Recipes

- **`mine_mvp`**: `lambertian_los`, `exp_extinction`, `markov`, `none` (multipath)

## 6. Space (`space`)

### Categories
- `free_space`, `tx_gain`, `rx_gain`, `pointing`, `atmospheric_entry`, `link_budget`

### Models

| Category | Model ID | Description |
| :--- | :--- | :--- |
| **free_space** | `fspl` | Friis path loss |
| **tx_gain** | `diffraction_limited` | Ideal diffraction limited gain |
| **rx_gain** | `telescope` | Telescope aperture gain |
| **pointing** | `gaussian` | Jitter penalty |
| | `none` | No pointing loss |
| **atmospheric_entry** | `none` | Deep space |
| | `beer_lambert` | Ground segment |
| **link_budget** | `multiplicative_chain` | Combiner |

### Recipes

- **`deep_space`**: `fspl`, `diffraction_limited`, `telescope`, `gaussian`, `none` (atm), `multiplicative_chain`
