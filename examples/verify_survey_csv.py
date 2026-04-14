from owcm import Channel
import numpy as np

def run_csv_validation():
    print("Test,Param,Value,Gain,Check")
    
    # 1. LoS Monotonicity & Retro Comparison
    d_vals = [1.0, 10.0, 20.0, 30.0, 40.0, 50.0]
    
    prev_los = float('inf')
    
    for d in d_vals:
        # LoS
        los_ch = Channel.environment("underwater") \
            .model("link", "los_case") \
            .build(distance_m=d, theta_rad=0.0, theta0_rad=0.174, attenuation_c=0.1, pt_w=1.0)
        g_los = los_ch.gain()
        
        # Retro
        retro_ch = Channel.environment("underwater") \
            .model("link", "retroreflective_case") \
            .build(distance_m=d, theta_rad=0.0, theta0_rad=0.174, 
                   theta0_retro_rad=0.01, ARetro_m2=0.01,
                   attenuation_c=0.1, pt_w=1.0)
        g_retro = retro_ch.gain()
        
        los_check = "PASS" if g_los < prev_los else "FAIL_Inc"
        comp_check = "PASS" if g_retro < g_los else "FAIL_RetroHigh"
        
        print(f"LoS_Retro,Distance,{d},{g_los:.4e},LoS_Monotonic:{los_check}")
        print(f"LoS_Retro,Distance,{d},{g_retro:.4e},Retro_Lower:{comp_check}")
        
        prev_los = g_los

    # 2. Reflective Continuity around Theta C
    n1, n2 = 1.33, 1.0
    theta_c = np.arcsin(n2/n1)
    
    # Test points close to critical angle
    eps = 1e-6
    points = [theta_c - eps, theta_c, theta_c + eps]
    labels = ["ThetaC-eps", "ThetaC", "ThetaC+eps"]
    
    vals = []
    
    for i, phi in enumerate(points):
        ref_ch = Channel.environment("underwater") \
            .model("nlos", "reflective_case") \
            .build(h_m=10, x_m=10, phi_rad=phi, theta_min_rad=0.0, theta_max_rad=1.5,
                   attenuation_c=0.1, pt_w=1.0)
        g = ref_ch.gain()
        vals.append(g)
        print(f"Continuity,{labels[i]},{phi:.6f},{g:.6e},Val")
        
    # Check simple continuity
    diff1 = abs(vals[1] - vals[0])
    diff2 = abs(vals[2] - vals[1])
    
    cont_check = "PASS" if (diff1 < 1e-9 and diff2 < 1e-9) else f"FAIL_Diff_{max(diff1,diff2):.2e}"
    print(f"Continuity,Check,N/A,N/A,{cont_check}")

if __name__ == "__main__":
    run_csv_validation()
