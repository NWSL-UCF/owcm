import csv
import os
import sys
from datetime import datetime

import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from owcm import Channel


def default_params_for_environment(env_name: str) -> dict:
    """Reasonable defaults so most registered models can run."""
    base = {
        "pt_w": 0.5,
        "wavelength_nm": 1550.0,
        "DR_m": 0.05,
        "DT_m": 0.05,
        "theta_rad": np.deg2rad(1.0),
        "fov_rad": np.pi / 2,
    }

    if env_name == "atmospheric":
        base.update(
            {
                "visibility_km": 2.0,
                "alpha": 0.05,
                "sigma_ln": 0.2,
                "gamma_alpha": 4.0,
                "gamma_beta": 3.0,
                "pointing_sigma_m": 0.02,
            }
        )
    elif env_name == "indoor":
        base.update(
            {
                "semi_angle_half_power_rad": np.deg2rad(60.0),
                "lambertian_order": 1.0,
                "concentrator_refractive_index": 1.5,
                "optical_filter_gain": 1.0,
                "reflectance": 0.7,
                "room_area_m2": 25.0,
                "n_bounces": 2,
                "p_blocked": 0.1,
                "p_01": 0.1,
                "p_10": 0.3,
            }
        )
    elif env_name == "underwater":
        base.update(
            {
                "wavelength_nm": 520.0,
                "attenuation_a": 0.1,
                "attenuation_b": 0.15,
                "attenuation_c": 0.25,
                "theta_rad": np.deg2rad(5.0),
                "theta0_rad": np.deg2rad(12.0),
                "etaT": 0.9,
                "etaR": 0.9,
                "etaRetro": 0.85,
                "ARetro_m2": 0.01,
                "theta0_retro_rad": np.deg2rad(0.7),
                "h_m": 8.0,
                "x_m": 10.0,
                "phi_rad": np.deg2rad(20.0),
                "theta_min_rad": np.deg2rad(5.0),
                "theta_max_rad": np.deg2rad(45.0),
                "n1": 1.33,
                "n2": 1.0,
            }
        )
    elif env_name == "underground":
        base.update(
            {
                "semi_angle_half_power_rad": np.deg2rad(60.0),
                "dust_conc_mg_m3": 3.0,
                "dust_k_per_m_per_mg_m3": 0.4,
                "p_blocked": 0.1,
                "p_01": 0.1,
                "p_10": 0.3,
            }
        )
    elif env_name == "space":
        base.update(
            {
                "wavelength_nm": 1550.0,
                "theta_rad": 10e-6,
                "DR_m": 0.3,
                "DT_m": 0.1,
                "eta_t": 0.8,
                "eta_r": 0.8,
            }
        )

    return base


def distance_grid_for_environment(env_name: str):
    if env_name == "indoor":
        return [1.0, 2.0, 5.0, 10.0]
    if env_name == "underwater":
        return [5.0, 10.0, 20.0, 30.0]
    if env_name == "underground":
        return [5.0, 10.0, 20.0, 40.0]
    if env_name == "space":
        return [1e3, 1e4, 5e4, 1e5]
    return [100.0, 500.0, 1000.0, 2000.0]  # atmospheric/default


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("outputs", f"channel_responses_{ts}")
    os.makedirs(out_dir, exist_ok=True)

    responses_path = os.path.join(out_dir, "responses.csv")
    errors_path = os.path.join(out_dir, "errors.csv")
    summary_path = os.path.join(out_dir, "summary.txt")

    response_rows = []
    error_rows = []

    environments = Channel.list_environments()
    for env_name in environments:
        env_builder = Channel.environment(env_name)
        model_map = env_builder.list_models()  # {category: [models]}

        params = default_params_for_environment(env_name)
        distances = distance_grid_for_environment(env_name)

        for category, model_names in model_map.items():
            for model_name in model_names:
                for d in distances:
                    kwargs = dict(params)
                    kwargs["distance_m"] = d
                    try:
                        ch = (
                            Channel.environment(env_name)
                            .model(category, model_name)
                            .build(**kwargs)
                        )
                        gain = float(ch.gain())
                        pr = float(ch.received_power())

                        # sample-based statistics at each distance
                        try:
                            s = ch.sample(2000)
                            s_mean = float(np.mean(s))
                            s_std = float(np.std(s))
                        except Exception:
                            s_mean = np.nan
                            s_std = np.nan

                        response_rows.append(
                            {
                                "environment": env_name,
                                "category": category,
                                "model": model_name,
                                "distance_m": d,
                                "gain": gain,
                                "received_power_w": pr,
                                "sample_mean": s_mean,
                                "sample_std": s_std,
                            }
                        )
                    except Exception as e:
                        error_rows.append(
                            {
                                "environment": env_name,
                                "category": category,
                                "model": model_name,
                                "distance_m": d,
                                "error": str(e),
                            }
                        )

    # Write CSV outputs
    with open(responses_path, "w", newline="", encoding="utf-8") as f:
        if response_rows:
            writer = csv.DictWriter(f, fieldnames=list(response_rows[0].keys()))
            writer.writeheader()
            writer.writerows(response_rows)
        else:
            f.write("environment,category,model,distance_m,gain,received_power_w,sample_mean,sample_std\n")

    with open(errors_path, "w", newline="", encoding="utf-8") as f:
        if error_rows:
            writer = csv.DictWriter(f, fieldnames=list(error_rows[0].keys()))
            writer.writeheader()
            writer.writerows(error_rows)
        else:
            f.write("environment,category,model,distance_m,error\n")

    # Simple summary
    total_attempts = len(response_rows) + len(error_rows)
    by_env = {}
    for row in response_rows:
        by_env[row["environment"]] = by_env.get(row["environment"], 0) + 1

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("OWCM Channel Response Sweep\n")
        f.write(f"Output directory: {out_dir}\n")
        f.write(f"Total attempts: {total_attempts}\n")
        f.write(f"Successful rows: {len(response_rows)}\n")
        f.write(f"Errors: {len(error_rows)}\n")
        f.write("\nSuccess counts by environment:\n")
        for env_name in sorted(by_env):
            f.write(f"  - {env_name}: {by_env[env_name]}\n")

    print(f"Saved responses: {responses_path}")
    print(f"Saved errors:    {errors_path}")
    print(f"Saved summary:   {summary_path}")


if __name__ == "__main__":
    main()

