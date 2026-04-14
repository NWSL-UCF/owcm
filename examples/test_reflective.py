from owcm import Channel
import numpy as np
import matplotlib.pyplot as plt

def run_reflective_demo():
    print("running Reflective NLoS Model Demo...")
    
    # We want to use our NEW model: "reflective_surface" in category "nlos"
    # The default "beer_lambert" recipe has 'scattering': 'none'.
    # We will build a custom channel.
    
    # 1. Define range of horizontal distances x
    x_vals = np.linspace(1, 50, 50)
    gains = []
    
    for x in x_vals:
        # Build channel
        # We override 'scattering' or 'nlos'? 
        # Registry says we added 'nlos' category.
        # But our Channel builder needs to know to LOOK for 'nlos'.
        # The defaulting mechanism only loads what is in the recipe.
        # If we use the builder with .model("nlos", "reflective_surface"), 
        # it will be added to the composite list.
        
        ch = Channel.environment("underwater") \
            .defaults("beer_lambert") \
            .model("nlos", "reflective_surface") \
            .build(
                x_m=x,
                h_m=5.0, # 5m depth
                attenuation_c=0.1,
                # Explicitly disable direct line of sight extinction if we ONLY want reflection?
                # No, usually we want Total = Direct + Reflected.
                # But here let's isolate Reflection to see it.
                # Set extinction model to 'none' ? Or a valid ID.
                # Let's just look at the TOTAL channel which will include BeerLambert (Direct) AND Reflective (NLoS).
                # Actually, composite multiplies. We want Sum. 
                # OWCM currently supports Multiplicative chains (Loss * Loss * Loss).
                # NLoS is usually a PARALLEL path (Direct + Reflected).
                # Limitation: The CompositeChannel multiplies gains. 
                # Use case: H_total = H_los + H_nlos...
                # workaround: The user asked to "cook a new model".
                # If they want ONLY the reflective path, they should disable the direct extinction part 
                # or treat this as the specific loss for a NLoS link.
                
                # Let's assume we are modeling a purely reflective link (blockage of LoS).
                # So we replace 'extinction' with 'none' (not avail?) or just ignore it.
                # Actually, the reflective model internally calculates L_pr (propagation loss).
                # So it is self-contained. 
                # effectively we want:
                # model = reflective_surface ONLY.
            )
            
        # Note: CompositeChannel multiplies factors. 
        # If we have [BeerLambert, Reflective], we get H = H_direct * H_reflective. 
        # That is WRONG for NLoS. 
        # H_reflective usually includes its own path loss.
        # So we should run the Reflective model ALONE for this demo, 
        # or clear the other models.
        
        # Clearing others by setting them to dummy 'none' or just using a raw build?
        # The builder accumulates from 'defaults'. 
        # Make a custom recipe? Or just overwrite.
        
        # Overwriting 'extinction' to 'none' (if we had a none model there).
        # We don't have 'none' for extinction in registry? 
        # Checklist: create a 'none' extinction if needed or just accept the multiply for the demo 
        # (interpreting as "Reflection Loss * Medium Attenuation"? No, reflection model has L_pr inside).
        
        # Proper way: Create a "pure_reflective" recipe.
        pass

    # Better approach for demo: manually instantiating for clarity? 
    # Or adding a "none" model to extinction for this test.
    # Let's use the API to clear the recipe.
    
    builder = Channel.environment("underwater")
    # Don't call defaults().
    # Manually set:
    builder.model("nlos", "reflective_surface")
    
    # Note: Builder requires at least some models? No.
    # But it won't have 'extinction' in the list.
    
    gains_ref = []
    for x in x_vals:
        ch = builder.build(
            x_m=x, 
            h_m=5.0, 
            attenuation_c=0.1,
            distance_m=1.0 # arbitrary, not used by reflective model which uses x, h
        )
        gains_ref.append(ch.gain())
        
    plt.figure()
    plt.semilogy(x_vals, gains_ref, label="Reflected Path")
    plt.xlabel("Horizontal Distance (m)")
    plt.ylabel("Channel Gain")
    plt.title("Underwater Surface Reflection (NLoS) Model")
    plt.grid(True)
    plt.legend()
    plt.savefig("reflective_demo.png")
    print("Saved reflective_demo.png")

if __name__ == "__main__":
    run_reflective_demo()
