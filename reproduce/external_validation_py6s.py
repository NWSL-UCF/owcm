from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from Py6S import (
    SixS,
    AtmosProfile,
    AeroProfile,
    Geometry,
    Altitudes,
    Wavelength,
    GroundReflectance,
)

from owcm import Channel


# ------------------------------------------------------------
# Validation configuration
# ------------------------------------------------------------

WAVELENGTHS_NM = np.array(
    [450, 550, 650, 850, 1064, 1550],
    dtype=float,
)

VISIBILITY_KM = 2.0
PATH_LENGTH_KM = 1.0
PATH_LENGTH_M = PATH_LENGTH_KM * 1000.0

OUTPUT_DIR = Path("reproduction_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# OWCM
# ------------------------------------------------------------

def run_owcm_kim(wavelength_nm):
    """
    Evaluate the OWCM Kim visibility-based attenuation model
    for a 1-km atmospheric optical link.
    """

    channel = (
        Channel.environment("atmospheric")
        .model("attenuation", "kim")
        .build(
            distance_m=PATH_LENGTH_M,
            wavelength_nm=float(wavelength_nm),
            visibility_km=VISIBILITY_KM,
        )
    )

    return float(channel.gain())


# ------------------------------------------------------------
# Py6S / 6S
# ------------------------------------------------------------

def run_py6s(wavelength_nm):
    """
    Evaluate upward atmospheric transmittance using 6S through
    Py6S.

    The target is placed at sea level and the sensor is placed
    1 km above it, creating an upward atmospheric propagation
    path of approximately 1 km.

    Maritime aerosols and 2-km visibility are used to provide
    an aerosol-rich atmospheric condition for comparison with
    the OWCM visibility-based attenuation model.
    """

    s = SixS()

    # Atmospheric profile
    s.atmos_profile = AtmosProfile.PredefinedType(
        AtmosProfile.MidlatitudeSummer
    )

    # Aerosol model
    s.aero_profile = AeroProfile.PredefinedType(
        AeroProfile.Maritime
    )

    # Use visibility rather than aerosol optical thickness
    s.aot550 = None
    s.visibility = VISIBILITY_KM

    # Vertical 1-km propagation path
    s.altitudes = Altitudes()
    s.altitudes.set_target_sea_level()
    s.altitudes.set_sensor_custom_altitude(
        PATH_LENGTH_KM
    )

    # Simple vertical geometry
    s.geometry = Geometry.User()
    s.geometry.solar_z = 0.0
    s.geometry.solar_a = 0.0
    s.geometry.view_z = 0.0
    s.geometry.view_a = 0.0
    s.geometry.month = 6
    s.geometry.day = 21

    # Surface reflectance is not the quantity being validated,
    # but is explicitly specified for reproducibility.
    s.ground_reflectance = (
        GroundReflectance.HomogeneousLambertian(0.2)
    )

    # Py6S wavelength is specified in micrometers
    s.wavelength = Wavelength(
        float(wavelength_nm) / 1000.0
    )

    s.run()

    scattering = float(
        s.outputs
        .transmittance_total_scattering
        .upward
    )

    gaseous = float(
        s.outputs
        .transmittance_global_gas
        .upward
    )

    combined = scattering * gaseous

    return scattering, gaseous, combined


# ------------------------------------------------------------
# Run comparison
# ------------------------------------------------------------

rows = []

for wavelength_nm in WAVELENGTHS_NM:

    owcm_gain = run_owcm_kim(
        wavelength_nm
    )

    (
        py6s_scattering,
        py6s_gaseous,
        py6s_combined,
    ) = run_py6s(
        wavelength_nm
    )

    absolute_difference = abs(
        owcm_gain - py6s_scattering
    )

    if py6s_scattering > 0:
        relative_difference = (
            absolute_difference
            / py6s_scattering
        )
    else:
        relative_difference = np.nan

    rows.append(
        {
            "wavelength_nm": wavelength_nm,
            "visibility_km": VISIBILITY_KM,
            "path_length_km": PATH_LENGTH_KM,
            "owcm_kim_transmittance": owcm_gain,
            "py6s_scattering_transmittance": py6s_scattering,
            "py6s_gaseous_transmittance": py6s_gaseous,
            "py6s_combined_transmittance": py6s_combined,
            "absolute_difference": absolute_difference,
            "relative_difference": relative_difference,
        }
    )


df = pd.DataFrame(rows)


# ------------------------------------------------------------
# Save numerical results
# ------------------------------------------------------------

csv_path = (
    OUTPUT_DIR
    / "external_validation_py6s.csv"
)

df.to_csv(
    csv_path,
    index=False,
)


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(7.5, 5.0)
)

ax.plot(
    df["wavelength_nm"],
    df["owcm_kim_transmittance"],
    marker="o",
    label="OWCM Kim model",
)

ax.plot(
    df["wavelength_nm"],
    df["py6s_scattering_transmittance"],
    marker="s",
    label="Py6S total scattering",
)

ax.plot(
    df["wavelength_nm"],
    df["py6s_combined_transmittance"],
    marker="^",
    linestyle="--",
    label="Py6S scattering × gaseous",
)

ax.set_xlabel(
    "Wavelength (nm)"
)

ax.set_ylabel(
    "Atmospheric Transmittance"
)

ax.set_ylim(
    bottom=0
)

ax.grid(
    True,
    alpha=0.3,
)

ax.legend()

fig.tight_layout()


png_path = (
    OUTPUT_DIR
    / "external_validation_py6s.png"
)

pdf_path = (
    OUTPUT_DIR
    / "external_validation_py6s.pdf"
)

fig.savefig(
    png_path,
    dpi=300,
    bbox_inches="tight",
)

fig.savefig(
    pdf_path,
    bbox_inches="tight",
)

plt.close(fig)


# ------------------------------------------------------------
# Console summary
# ------------------------------------------------------------

print("\nOWCM / Py6S External Validation")
print("=" * 70)

print(
    f"Visibility: {VISIBILITY_KM:.1f} km"
)

print(
    f"Propagation distance: "
    f"{PATH_LENGTH_KM:.1f} km"
)

print()

print(
    df.to_string(
        index=False
    )
)

print("\nGenerated files:")

print(
    f"  {csv_path}"
)

print(
    f"  {png_path}"
)

print(
    f"  {pdf_path}"
)

print(
    "\nInterpretation:"
)

print(
    "OWCM Kim is a reduced-order visibility-based "
    "communication model, whereas 6S resolves "
    "atmospheric scattering and gaseous effects in "
    "greater physical detail. Exact numerical agreement "
    "is therefore not expected."
)
