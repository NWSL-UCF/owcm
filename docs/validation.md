# OWCM Numerical Validation and Tolerance Policy

This document defines the numerical validation criteria used for the Optical Wireless Communication Channel Model (OWCM) library. The purpose is to make implementation verification reproducible and to distinguish numerical round-off error from physically meaningful disagreement.

OWCM contains both deterministic analytical models and stochastic channel models. Different validation criteria are therefore required for these two classes.

## 1. General Principles

Validation tests compare OWCM outputs against one or more of the following:

1. closed-form analytical calculations;
2. known physical scaling laws;
3. published reference equations;
4. statistical properties of theoretical probability distributions; or
5. independent reference software when available.

A test is considered successful when the OWCM result satisfies the tolerance specified for the corresponding validation category.

The tolerances defined here are numerical verification criteria. They do not represent uncertainty in the underlying physical channel model.

---

## 2. Deterministic Analytical Models

For deterministic closed-form expressions, OWCM uses numerical comparison based on

\[
\left|x_{\mathrm{OWCM}}-x_{\mathrm{ref}}\right|
\leq
\mathrm{atol}
+
\mathrm{rtol}\left|x_{\mathrm{ref}}\right|,
\]

where:

- \(x_{\mathrm{OWCM}}\) is the value produced by OWCM;
- \(x_{\mathrm{ref}}\) is the analytical reference value;
- `rtol` is the relative tolerance; and
- `atol` is the absolute tolerance.

Unless otherwise justified for a particular model, the default deterministic validation tolerances are

```text
relative tolerance (rtol) = 1e-6
absolute tolerance (atol) = 1e-12
```

These tolerances are intended for equations implemented directly using standard floating-point arithmetic.

Example:

```python
import numpy as np

np.testing.assert_allclose(
    calculated,
    expected,
    rtol=1e-6,
    atol=1e-12,
)
```

---

## 3. Physical Scaling Tests

Some channel models are more appropriately verified using known physical scaling behavior rather than exact numerical equality.

Examples include:

\[
h_{\mathrm{fs}}\propto R^{-2}
\]

for free-space propagation and

\[
G_R\propto D_R^2
\]

for receiver-aperture gain under the corresponding assumptions.

For scaling-law tests, a relative deviation of

```text
10%
```

is permitted unless a tighter model-specific tolerance is documented.

The larger tolerance accounts for comparisons involving ratios, numerical approximations, or simplified engineering models rather than direct evaluation of an identical analytical expression.

---

## 4. Stochastic Models

Stochastic channel models cannot be validated by requiring individual random samples to equal theoretical values.

Instead, OWCM validates statistical properties obtained from a sufficiently large Monte Carlo sample.

A fixed random seed must be used in reproducibility tests.

Example:

```python
samples = channel.sample(
    n=100000,
    rng=42,
)
```

The following default criteria are used.

### 4.1 Mean

For models normalized to unit mean,

\[
E[I]=1,
\]

the simulated sample mean should satisfy

\[
\left|\hat{\mu}-1\right| < 0.02.
\]

Thus, a default tolerance of approximately **2%** is used for the sample mean when \(n=100000\).

---

### 4.2 Variance

When a theoretical variance is available, the relative error between simulated and theoretical variance should satisfy

\[
\frac{
\left|
\hat{\sigma}^2-\sigma_{\mathrm{theory}}^2
\right|
}{
\sigma_{\mathrm{theory}}^2
}
<0.05.
\]

A default relative tolerance of **5%** is therefore used for variance-based stochastic validation with sufficiently large sample sizes.

---

### 4.3 Distribution-Level Validation

Where appropriate, the empirical distribution may additionally be compared with its theoretical CDF or PDF.

Possible validation methods include:

- Kolmogorov–Smirnov testing;
- comparison of empirical and theoretical quantiles;
- comparison of outage probabilities; and
- comparison of empirical and analytical moments.

Distribution-specific acceptance criteria should be documented in the corresponding test.

---

## 5. Monte Carlo Sample Size

Unless a model-specific justification is provided, stochastic validation should use at least

```text
n = 100000
```

samples.

A fixed seed such as

```text
rng = 42
```

should be used so that the validation result is reproducible.

Larger sample sizes may be required for rare-event or deep-fade probability calculations.

---

## 6. Outage Probability

For stochastic channels, outage probability is defined as

\[
P_{\mathrm{out}}
=
\Pr(P_R<P_{\mathrm{th}}).
\]

When an analytical outage probability is available, the Monte Carlo estimate is compared against it.

For ordinary-probability validation, the default acceptance criterion is

\[
\left|
\hat{P}_{\mathrm{out}}
-
P_{\mathrm{out,ref}}
\right|
<0.01.
\]

This corresponds to an absolute probability tolerance of **0.01**.

This default is not intended for very small rare-event probabilities, for which larger Monte Carlo sample sizes or specialized simulation methods may be required.

---

## 7. Neutral-Loss and Boundary Tests

Models containing multiplicative loss factors should satisfy expected physical boundaries.

Examples include:

```text
0 <= channel gain <= 1
```

for pure attenuation factors where amplification is physically excluded.

Neutral parameters should recover their expected limiting behavior. Examples include:

```text
attenuation coefficient = 0  -> attenuation gain = 1
pointing displacement = 0    -> maximum pointing gain
blockage probability = 0     -> no blockage loss
loss factor = 1              -> no additional loss
```

These tests normally use the deterministic tolerances defined in Section 2.

---

## 8. Beer–Lambert Validation

For

\[
h=\exp(-\alpha R),
\]

OWCM output should agree directly with the analytical calculation using

```text
rtol = 1e-6
atol = 1e-12
```

The following limiting cases should also hold:

\[
\alpha=0
\quad\Rightarrow\quad
h=1,
\]

and

\[
R=0
\quad\Rightarrow\quad
h=1.
\]

---

## 9. Free-Space Loss Validation

For

\[
h_{\mathrm{fs}}
=
\left(
\frac{\lambda}{4\pi R}
\right)^2,
\]

direct numerical evaluation should use

```text
rtol = 1e-6
atol = 1e-12
```

The distance-scaling relation

\[
h_{\mathrm{fs}}\propto R^{-2}
\]

should additionally be verified.

For example, doubling propagation distance should yield approximately

\[
\frac{h(2R)}{h(R)}=\frac{1}{4}.
\]

---

## 10. Lambertian Channel Validation

Indoor Lambertian LoS models should be checked against direct evaluation of the corresponding analytical DC-gain expression.

For identical equations and parameter values:

```text
rtol = 1e-6
atol = 1e-12
```

Boundary behavior associated with the receiver field of view should also be verified:

- incidence angle inside the FOV: nonzero gain may occur;
- incidence angle outside the FOV: gain should be zero.

---

## 11. Gamma–Gamma Validation

Gamma–Gamma samples are generated using the product of large-scale and small-scale Gamma random variables.

For normalized Gamma–Gamma fading, the principal validation criterion is

\[
E[I]\approx1.
\]

For

```text
n = 100000
```

the default acceptance criterion is

```text
abs(sample_mean - 1.0) < 0.02
```

Additional variance or distribution-level tests may be introduced using the theoretical Gamma–Gamma moments corresponding to the selected \(\alpha\) and \(\beta\).

---

## 12. Log-Normal Validation

For a unit-mean log-normal implementation, the distribution parameters are selected so that

\[
E[I]=1.
\]

For

```text
n = 100000
```

the default mean criterion is

```text
abs(sample_mean - 1.0) < 0.02
```

The simulated variance may additionally be compared against the theoretical log-normal variance using a relative tolerance of approximately 5%.

---

## 13. Blockage Models

For an independent on–off blockage model with blockage probability \(p_b\), the expected mean channel gain is

\[
E[h]=1-p_b.
\]

For Monte Carlo validation with \(n=100000\),

```text
abs(sample_mean - (1 - p_blocked)) < 0.01
```

is used as the default criterion.

For two-state Markov blockage, long-run simulated state occupancy may be compared against the theoretical stationary probability

\[
P_{\mathrm{unblocked}}
=
\frac{p_{10}}
{p_{01}+p_{10}}.
\]

---

## 14. Reproducibility Requirements for Tests

Every stochastic validation test should record:

- sample size;
- random seed;
- model parameters;
- expected theoretical quantity; and
- acceptance tolerance.

Example:

```python
N_SAMPLES = 100000
RNG_SEED = 42
MEAN_TOL = 0.02
```

Numerical constants used exclusively as validation tolerances should be named explicitly rather than embedded as unexplained values inside test expressions.

---

## 15. Model-Specific Exceptions

The default tolerances in this document may be relaxed or tightened when justified by:

- numerical integration;
- iterative calculations;
- Monte Carlo uncertainty;
- approximate analytical models;
- interpolation;
- comparison against independent software; or
- empirical/model-fitting uncertainty.

Any model-specific tolerance different from the defaults must include a brief explanation in the corresponding test or validation documentation.

---

## 16. Summary of Default Validation Criteria

| Validation type | Default criterion |
|---|---|
| Direct deterministic equation | `rtol = 1e-6`, `atol = 1e-12` |
| Engineering/scaling relation | approximately 10% relative tolerance |
| Unit-mean stochastic model | absolute mean error < 0.02 |
| Stochastic variance | relative error < 5% |
| Outage probability | absolute error < 0.01 |
| Monte Carlo validation size | \(n \ge 100000\) |
| Default reproducibility seed | 42 |

These values provide a common starting point for OWCM verification. Individual models may define stricter or model-specific criteria when appropriate.
