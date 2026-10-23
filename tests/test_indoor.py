import numpy as np

from owcm.core.types import Link, Tx, Rx, Environment
from owcm.indoor.models.all_models import (
    IndoorLambertianLoS,
    OnOffBlockage,
    MarkovBlockage,
)

RTOL = 1e-6
ATOL = 1e-12
N = 100000
SEED = 42


def make_link(
    distance_m=3.0,
    dr_m=0.01,
    fov_rad=np.pi / 2,
):
    tx = Tx(wavelength_nm=850.0)

    rx = Rx(
        aperture_diameter_m=dr_m,
        field_of_view_rad=fov_rad,
    )

    rx.position = np.array(
        [0.0, 0.0, distance_m]
    )

    return Link(tx=tx, rx=rx)


def test_lambertian_los_matches_aligned_closed_form():
    link = make_link(
        distance_m=3.0,
        dr_m=0.01,
    )

    env = Environment(name="indoor")

    model = IndoorLambertianLoS(
        link,
        env,
        lambertian_order=1.0,
    )

    area = np.pi * (0.01 / 2.0) ** 2

    radiant_intensity = (
        (1.0 + 1.0)
        / (2.0 * np.pi)
    )

    expected = (
        (area / 3.0**2)
        * radiant_intensity
    )

    np.testing.assert_allclose(
        model.gain(link, env),
        expected,
        rtol=RTOL,
        atol=ATOL,
    )


def test_lambertian_gain_is_zero_outside_fov():
    link = make_link(
        fov_rad=np.deg2rad(30.0)
    )

    env = Environment(
        name="indoor",
        params={
            "cos_phi": 1.0,
            "cos_psi": 0.5,
        },
    )

    model = IndoorLambertianLoS(
        link,
        env,
        lambertian_order=1.0,
    )

    assert model.gain(link, env) == 0.0


def test_onoff_blockage_mean_matches_probability():
    link = make_link()
    env = Environment(name="indoor")

    p_blocked = 0.25

    model = OnOffBlockage(
        link,
        env,
        p_blocked=p_blocked,
    )

    samples = model.sample(
        link,
        env,
        N,
        rng=SEED,
    )

    assert (
        abs(
            np.mean(samples)
            - (1.0 - p_blocked)
        )
        < 0.01
    )


def test_markov_blockage_mean_matches_stationary_probability():
    link = make_link()
    env = Environment(name="indoor")

    p_01 = 0.1
    p_10 = 0.3

    model = MarkovBlockage(
        link,
        env,
        p_01=p_01,
        p_10=p_10,
    )

    expected = (
        p_10
        / (p_01 + p_10)
    )

    samples = model.sample(
        link,
        env,
        N,
        rng=SEED,
    )

    assert abs(
        np.mean(samples) - expected
    ) < 0.02
