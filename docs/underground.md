# Underground Optical Wireless Channel Models

This document describes the underground optical/VLC models implemented in OWCM, aligned with the updated `FSO_Survey.pdf` (Section VII).

---

## 1. Overview

Underground optical links (especially in mining tunnels) face:

- complex tunnel geometry and irregular reflective surfaces,
- airborne dust scattering/attenuation,
- blockage/shadowing from machinery and workers,
- misalignment due to mounting and tunnel deformation.

The implemented OWCM underground channel is a practical multiplicative model:

\[
H_{\text{total}} = H_{\text{LoS}} \cdot H_{\text{dust}} \cdot H_{\text{blockage}} \cdot H_{\text{multipath}}
\]

---

## 2. Available Models

Defined in `owcm/underground/models/all_models.py`.

### 2.1 LoS

#### `lambertian_los` (category: `los`)

Current implementation uses a simple inverse-square baseline:

\[
H_{\text{LoS}} \approx \frac{1}{R^2}
\]

This is a compact approximation to underground LoS behavior (survey Eq. 57 style LoS dependence on distance, with simplified angular terms).

---

### 2.2 Dust

#### `exp_extinction` (category: `dust`)

Exponential dust attenuation model:

\[
H_{\text{dust}} = \exp(-k C R)
\]

where:
- \(C\): dust concentration (mg/m\(^3\)),
- \(k\): specific extinction coefficient per (mg/m\(^3\)),
- \(R\): link range.

#### `none` (category: `dust`)

No dust attenuation (\(H=1\)).

---

### 2.3 Blockage

#### `none` (category: `blockage`)

No blockage (\(H=1\)).

#### `onoff`

Binary blockage:
- unblocked: gain \(=1\)
- blocked: gain \(=0\)

`gain()` returns average:
\[
\mathbb{E}[H] = 1 - p_{\text{blocked}}
\]

`sample(n)` returns Bernoulli sequence of 0/1 gains.

#### `markov`

Two-state Markov blockage:
- state 0: unblocked (gain 1)
- state 1: blocked (gain 0)

Transition probabilities:
- \(p_{01}=P(0\rightarrow1)\)
- \(p_{10}=P(1\rightarrow0)\)

Steady-state mean gain:
\[
\mathbb{E}[H] = \frac{p_{10}}{p_{01}+p_{10}}
\]

`sample(n)` returns correlated 0/1 blockage traces.

---

### 2.4 Multipath

#### `none` (category: `multipath`)

No multipath factor (\(H=1\)).

#### `kbounce`

Currently a placeholder equivalent to no-loss (\(H=1\)).
Use `none`/`kbounce` interchangeably until a detailed tunnel-wall reflection model is added.

---

## 3. Recipe

Configured in `owcm/underground/recipes.py`:

| Recipe | Components | Description |
|---|---|---|
| `mine_mvp` | `los=lambertian_los`, `dust=exp_extinction`, `blockage=markov`, `multipath=none` | Default underground mining setup |

---

## 4. Parameter Reference

All parameters are passed through `.build(**kwargs)`.

### 4.1 Common Builder Parameters

| Parameter | Unit | Default | Meaning |
|---|---:|---:|---|
| `distance_m` | m | 1000.0 | Tx–Rx distance \(R\) |
| `DR_m` | m | 0.1 | Rx aperture diameter |
| `pt_dbm` | dBm | 0.0 | Tx power in dBm |
| `pt_w` | W | — | Tx power in W (overrides `pt_dbm`) |
| `wavelength_nm` | nm | 1550.0 | Wavelength |

### 4.2 Dust Model Parameters (`exp_extinction`)

| Parameter | Unit | Default | Meaning |
|---|---:|---:|---|
| `dust_conc_mg_m3` | mg/m\(^3\) | 0.0 | Dust concentration \(C\) |
| `dust_k_per_m_per_mg_m3` | 1/m per (mg/m\(^3\)) | 0.5 | Dust specific extinction \(k\) |

### 4.3 Blockage Parameters

#### On-off blockage

| Parameter | Default | Meaning |
|---|---:|---|
| `p_blocked` | 0.1 | Blockage probability |

#### Markov blockage

| Parameter | Default | Meaning |
|---|---:|---|
| `p_01` | 0.1 | \(P(\text{unblocked} \rightarrow \text{blocked})\) |
| `p_10` | 0.3 | \(P(\text{blocked} \rightarrow \text{unblocked})\) |

---

## 5. Usage Examples

### 5.1 Default underground recipe (`mine_mvp`)

```python
from owcm import Channel

ch = Channel.environment("underground").defaults("mine_mvp").build(
    distance_m=25.0,
    DR_m=0.02,
    dust_conc_mg_m3=3.0,
    dust_k_per_m_per_mg_m3=0.4,
    p_01=0.08,
    p_10=0.20
)

print("mean gain:", ch.gain())
print("received power [W]:", ch.received_power())
```

### 5.2 Force on–off blockage (instead of Markov)

```python
from owcm import Channel

ch = (
    Channel.environment("underground")
    .defaults("mine_mvp")
    .model("blockage", "onoff")
    .build(
        distance_m=20.0,
        dust_conc_mg_m3=2.0,
        p_blocked=0.15
    )
)

print("mean gain:", ch.gain())
print("sampled gains:", ch.sample(20))
```

### 5.3 No dust sensitivity run

```python
from owcm import Channel

ch = (
    Channel.environment("underground")
    .defaults("mine_mvp")
    .model("dust", "none")
    .build(distance_m=20.0, p_01=0.1, p_10=0.3)
)

print("gain without dust:", ch.gain())
```

### 5.4 Outage simulation

```python
from owcm import Channel

ch = Channel.environment("underground").defaults("mine_mvp").build(
    distance_m=30.0,
    dust_conc_mg_m3=4.0,
    p_01=0.12,
    p_10=0.22
)

p_out = ch.outage(threshold_w=1e-9, n=100_000)
print("outage probability:", p_out)
```

---

## 6. Notes on Scope and Extensions

- Current underground implementation is intentionally compact and robust for simulation pipelines.
- `lambertian_los` is simplified (distance-dominant).
- `kbounce` under `multipath` is currently a placeholder.
- Next upgrade path:
  - full Lambertian angular LoS (irradiance/incidence/FOV/filter/concentrator),
  - geometry-aware tunnel-wall reflection integration (survey Eq. 60 style),
  - explicit dust-scattering term added as separate factor \(H_{\text{scat}}\).

---

## 7. References

- `FSO_Survey.pdf`, Section VII (Underground)
- Underground analytical discussion: Lambertian LoS, reflected NLoS, dust/scattering and blockage effects.
