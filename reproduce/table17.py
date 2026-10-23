from pathlib import Path
import csv

OUTDIR = Path("reproduction_outputs")
OUTDIR.mkdir(exist_ok=True)

rows = [
    ("Tx Power PT", "0.1 W (~20 dBm)", "All"),
    ("Wavelength lambda", "1550 nm (FSO/space); 850 nm (indoor); 488-532 nm (underwater); 550 nm (underground)", "a-f"),
    ("Apertures DT, DR", "2-10 cm typical; DR swept from 5-20 cm for aperture-gain analysis", "a-f"),
    ("Beam divergence theta", "~1 mrad", "a"),
    ("Visibility V", "2 km", "a"),
    ("Extinction coefficient c(lambda)", "0.05-0.40 m^-1", "c,d"),
    ("Dust concentration C", "0.2 mg/m^3", "e"),
    ("Dust attenuation", "alpha_d = kC, with k = 0.15 -> alpha_d = 0.03 m^-1", "e"),
    ("Lambertian order m", "1", "b,e"),
    ("Field of view", "60 deg receiver half-angle", "b,e"),
    ("Reflectivity rho", "0.7", "b"),
    ("Blockage probability p_b", "0.1, 0.3", "e"),
    ("Efficiency eta_T, eta_R", "~0.9", "c,d,f"),
    ("Scattering", "Neglected; dominant absorption/extinction focus", "c,d,e"),
]

path = OUTDIR / "table17_parameters.csv"
with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Parameter", "Value / Description", "Figure panel"])
    writer.writerows(rows)

print(f"Created {path}")
