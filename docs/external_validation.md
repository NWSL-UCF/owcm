# External Validation of OWCM

This document describes comparison of the Optical Wireless Communication Channel Model (OWCM) library with an established external radiative-transfer tool.

## Reference Tool

Atmospheric propagation is compared with the Second Simulation of a Satellite Signal in the Solar Spectrum (6S) radiative-transfer model through its Python interface, Py6S.

Py6S provides access to detailed atmospheric quantities including gaseous transmittance, Rayleigh-scattering transmittance, aerosol-scattering transmittance, and total atmospheric scattering transmittance.

The comparison is intended to evaluate the range of validity of OWCM rather than to claim numerical equivalence between the two frameworks.

## Scope of the Comparison

OWCM and 6S address different modeling objectives.

OWCM is designed primarily for optical wireless communication channel analysis. Its atmospheric module combines simplified analytical and statistical components such as

- Beer–Lambert attenuation;
- visibility-based fog models;
- turbulence fading;
- pointing error;
- beam geometry; and
- receiver aperture effects.

In contrast, 6S is a radiative-transfer model developed for atmospheric propagation and remote-sensing applications. It provides more detailed treatment of wavelength-dependent molecular absorption and atmospheric scattering.

Therefore, only overlapping atmospheric-transmittance behavior is considered in this comparison.

## Comparison Quantities

The external comparison considers

1. atmospheric transmission versus wavelength;
2. total scattering transmittance;
3. gaseous transmittance;
4. aerosol and Rayleigh-scattering contributions; and
5. the equivalent attenuation represented by the simplified OWCM channel.

The 6S/Py6S outputs used for comparison include

```text
total_gaseous_transmittance
transmittance_rayleigh_scattering
transmittance_aerosol_scattering
transmittance_total_scattering
```

## Interpretation

Exact agreement between OWCM and 6S is not expected because the two tools model atmospheric propagation at different levels of physical detail.

Agreement in broad attenuation trends provides confidence that the simplified OWCM atmospheric channel behaves consistently with established radiative-transfer physics within its intended operating regime.

Differences are expected when molecular absorption, wavelength-selective atmospheric gases, multiple scattering, aerosol-profile details, or vertically varying atmospheric properties become important.

## Implementation Limits Exposed by the Comparison

The comparison highlights several deliberate limitations of the current OWCM atmospheric implementation:

- OWCM visibility-based fog models use reduced-order empirical attenuation expressions.
- OWCM does not perform full spectral molecular radiative transfer.
- OWCM does not model detailed altitude-dependent aerosol profiles in the same manner as 6S.
- Multiple scattering is not explicitly resolved by the simplified Beer–Lambert implementation.
- OWCM includes communication-specific effects such as turbulence fading, pointing error, beam divergence, aperture coupling, and outage analysis that are outside the primary purpose of 6S.

Thus, OWCM should not be interpreted as a replacement for a full atmospheric radiative-transfer solver.

Instead, OWCM provides a computationally lightweight framework for communication-oriented channel analysis in which detailed radiative-transfer results may be incorporated when required.

## Reproducibility

The external validation uses

```text
Py6S 1.9.2
```

with the corresponding 6S executable.

The validation environment is recorded separately from the core OWCM environment because Py6S is used only for independent benchmarking and is not required to operate OWCM.

The comparison script is provided in

```text
reproduce/external_validation_py6s.py
```

and the resulting numerical outputs and figures should be retained with the permanent OWCM release.

## Conclusion

The external comparison is intended to establish two points:

1. the simplified OWCM atmospheric implementation follows physically consistent attenuation trends within its intended regime; and
2. detailed radiative-transfer tools remain necessary when wavelength-dependent molecular absorption, complex aerosol scattering, or other higher-fidelity atmospheric processes must be resolved.

This distinction defines the implementation boundary of OWCM and prevents the library from being interpreted as a substitute for specialized radiative-transfer software.
