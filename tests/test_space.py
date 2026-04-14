import numpy as np
import os
# import pytest
import csv
from owcm.core.types import Link, Tx, Rx, Environment
from owcm.space.models.deepspace import DeepSpaceTableXIII

RESULTS_DIR = "results"

def setup_module(module):
    os.makedirs(RESULTS_DIR, exist_ok=True)

def test_fspl_slope():
    """
    Test 1 — FSPL slope ≈ −2
    """
    # Setup
    wavelength_nm = 1550.0
    w0_rad = 50e-6
    dr = 0.1
    sigma_p = 0.0
    
    # Sweep
    ranges = [1e9, 2e9, 5e9, 1e10]
    received_powers = []
    
    # We need to simulate Pr = Pt * H.
    # User didn't specify Pt for independent check, but H = Pr/Pt.
    # So Pr = H * Pt. Let's assume Pt = 1.0 W (30 dBm).
    pt_watts = 1.0
    pt_dbm = 30.0
    
    print("\n--- Test 1: FSPL Slope ---")
    results = []
    
    for r in ranges:
        tx = Tx(power_dbm=pt_dbm, wavelength_nm=wavelength_nm)
        # Position tx at origin, rx at distance r on z-axis
        tx.position = np.array([0.0, 0.0, 0.0])
        rx = Rx(aperture_diameter_m=dr)
        rx.position = np.array([0.0, 0.0, r])
        
        link = Link(tx=tx, rx=rx)
        env = Environment(name="DeepSpace")
        
        model = DeepSpaceTableXIII(link, env, w0_rad=w0_rad, sigma_p=sigma_p)
        gain = model.gain(link, env)
        pr = pt_watts * gain
        received_powers.append(pr)
        results.append((r, pr))
        print(f"R={r:.1e} m, Pr={pr:.4e} W")
        
    # Compute slope
    log_r = np.log10(ranges)
    log_pr = np.log10(received_powers)
    
    slope, intercept = np.polyfit(log_r, log_pr, 1)
    print(f"Slope: {slope}")
    
    # Export CSV
    csv_path = os.path.join(RESULTS_DIR, "space_pr_vs_distance.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Range_m", "received_power_W"])
        writer.writerows(results)
        
    # Assert
    assert abs(slope + 2) < 0.1, f"Slope {slope} is not close to -2"

def test_receiver_aperture_scaling():
    """
    Test 2 — Receiver aperture scaling
    """
    # Setup
    wavelength_nm = 1550.0
    w0_rad = 50e-6
    sigma_p = 0.0
    range_m = 1e9 # Fixed R
    
    drs = [0.05, 0.1, 0.2]
    pr_values = {}
    pt_watts = 1.0
    pt_dbm = 30.0
    
    print("\n--- Test 2: Aperture Scaling ---")
    results = []
    
    for dr in drs:
        tx = Tx(power_dbm=pt_dbm, wavelength_nm=wavelength_nm)
        tx.position = np.array([0.0, 0.0, 0.0])
        rx = Rx(aperture_diameter_m=dr)
        rx.position = np.array([0.0, 0.0, range_m])
        
        link = Link(tx=tx, rx=rx)
        env = Environment(name="DeepSpace")
        
        model = DeepSpaceTableXIII(link, env, w0_rad=w0_rad, sigma_p=sigma_p)
        gain = model.gain(link, env)
        pr = pt_watts * gain
        pr_values[dr] = pr
        results.append((dr, pr))
        print(f"Dr={dr} m, Pr={pr:.4e} W")

    # Check ratios
    ratio1 = pr_values[0.2] / pr_values[0.1]
    ratio2 = pr_values[0.1] / pr_values[0.05]
    
    print(f"Pr(0.2)/Pr(0.1) = {ratio1}")
    print(f"Pr(0.1)/Pr(0.05) = {ratio2}")
    
    # Export CSV
    csv_path = os.path.join(RESULTS_DIR, "space_aperture_gain.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["aperture_diameter_m", "received_power_W"])
        writer.writerows(results)
        
    # Tolerance +- 10%
    # Expectation: Area scales with D^2. Power scales with Area.
    # So double Diameter -> 4x Area -> 4x Power? 
    # Formula: G_r = (pi Dr / lambda)^2 ... scales with Dr^2. Yes.
    
    assert abs(ratio1 - 4.0) < 0.4, f"Ratio1 {ratio1} not close to 4" # 10% of 4 is 0.4
    assert abs(ratio2 - 4.0) < 0.4, f"Ratio2 {ratio2} not close to 4"

if __name__ == "__main__":
    # Allow running directly
    setup_module(None)
    test_fspl_slope()
    test_receiver_aperture_scaling()
    print("All tests passed!")
