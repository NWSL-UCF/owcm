from owcm import Channel
import numpy as np
import matplotlib.pyplot as plt

def run_survey_checks():
    print("Running Survey Model Sanity Checks...")
    
    # 1. LoS Monotonicity (los_case)
    d_vals = np.linspace(1, 50, 50)
    los_gains = []
    
    for d in d_vals:
        builder = Channel.environment("underwater")
        builder.model("link", "los_case") 
        
        ch = builder.build(
            distance_m=d,
            theta_rad=0.0,
            theta0_rad=0.174, # 10 deg
            attenuation_c=0.1,
            pt_w=1.0
        )
        los_gains.append(ch.gain())
        
    plt.figure()
    plt.semilogy(d_vals, los_gains, 'b-', label="LoS (Eq 89)")
    
    # 2. Retro Comparison (retroreflective_case)
    retro_gains = []
    for d in d_vals:
        builder = Channel.environment("underwater")
        builder.model("link", "retroreflective_case")
        ch = builder.build(
            distance_m=d,
            theta_rad=0.0,
            theta0_rad=0.174,
            theta0_retro_rad=0.01,
            ARetro_m2=0.01,
            attenuation_c=0.1,
            pt_w=1.0
        )
        retro_gains.append(ch.gain())
        
    plt.semilogy(d_vals, retro_gains, 'r--', label="Retro (Eq 90)")
    plt.title("LoS vs Retro (Survey Model)")
    plt.xlabel("Distance d (m)")
    plt.ylabel("Gain")
    plt.legend()
    plt.grid(True)
    plt.savefig("survey_model_check.png")
    print("Saved survey_model_check.png")
    
    # 3. Reflective Continuity (reflective_case)
    n1, n2 = 1.33, 1.0
    theta_c = np.arcsin(n2/n1) # ~48.75 deg
    print(f"Theta Critical: {theta_c:.4f} rad")
    
    phis = np.linspace(theta_c - 0.2, theta_c + 0.2, 100)
    ref_gains = []
    
    for phi in phis:
        builder = Channel.environment("underwater")
        builder.model("nlos", "reflective_case")
        ch = builder.build(
            h_m=10, x_m=10,
            phi_rad=phi,
            theta_min_rad=0.0,
            theta_max_rad=1.5,
            attenuation_c=0.1,
            pt_w=1.0
        )
        ref_gains.append(ch.gain())
        
    plt.figure()
    plt.plot(np.degrees(phis), ref_gains, 'g-')
    plt.axvline(np.degrees(theta_c), color='k', linestyle='--', label='Critical Angle')
    plt.title("Reflective Gain vs Phi (Continuity Check)")
    plt.xlabel("Phi (deg)")
    plt.ylabel("Gain")
    plt.legend()
    plt.grid(True)
    plt.savefig("survey_model_continuity.png")
    print("Saved survey_model_continuity.png")

if __name__ == "__main__":
    run_survey_checks()
