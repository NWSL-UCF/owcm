from owcm import Channel
import numpy as np

def run():
    print("--- OWC Library Demo ---")
    
    # 1. Atmospheric
    print("\n[Atmospheric Channel]")
    ch_atm = Channel.environment("atmospheric").defaults("mvp").build(
        distance_m=1000, wavelength_nm=1550, pt_w=0.5,
        visibility_km=2.0,
        theta_rad=1e-3, DT_m=0.05, DR_m=0.1,
        gg_alpha=3.2, gg_beta=2.1,
        jitter_sigma_m=0.01, wz_eq_m=0.08
    )
    
    pr = ch_atm.received_power()
    print(f"Received Power: {pr:.3e} W")
    
    outage = ch_atm.outage(threshold_w=1e-6, n=10000)
    print(f"Outage Prob (<1uW): {outage:.4f}")
    
    # 2. Indoor
    print("\n[Indoor Channel]")
    ch_in = Channel.environment("indoor").defaults("los").build(
        distance_m=3.0, lambertian_order=1.0, DR_m=0.01
    )
    print(f"Indoor Gain: {ch_in.gain():.3e}")

    # 3. Underwater
    print("\n[Underwater Channel]")
    ch_uw = Channel.environment("underwater").defaults("beer_lambert").build(
        distance_m=10.0, attenuation_c=0.1
    )
    print(f"Underwater Gain: {ch_uw.gain():.3e}")

if __name__ == "__main__":
    run()
