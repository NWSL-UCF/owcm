import numpy as np

from owcm.core.types import Link, Tx, Rx, Environment
from owcm.atmospheric.models.attenuation import (
    BeerLambertAttenuation,
    KimFogModel,
)
from owcm.atmospheric.models.turbulence import (
    LogNormalTurbulence,
    GammaGammaTurbulence,
)
from owcm.atmospheric.models.pointing import (
    RayleighGaussianPointingLoss,
)

RTOL = 1e-6
ATOL = 1e-12
N = 100000
SEED = 42


def make_link(distance_m=1000.0, wavelength_nm=1550.0, dr_m=0.1):
    tx = Tx(wavelength_nm=wavelength_nm)
    rx = Rx(aperture_diameter_m=dr_m)
    rx.position = np.array([0.0, 0.0, distance_m])
    return Link(tx=tx, rx=rx)


def test_beer_lambert_matches_closed_form():
    link = make_link(distance_m=1200.0)
    env = Environment(name="atmospheric")
    alpha = 2.5e-4

    model = BeerLambertAttenuation(
        link,
        env,
        alpha=alpha,
    )

    expected = np.exp(-alpha * link.range_m)

    np.testing.assert_allclose(
        model.gain(link, env),
        expected,
        rtol=RTOL,
        atol=ATOL,
    )


def test_beer_lambert_zero_attenuation_is_unity():
    link = make_link()
    env = Environment(name="atmospheric")

    model = BeerLambertAttenuation(
        link,
        env,
        alpha=0.0,
    )

    np.testing.assert_allclose(
        model.gain(link, env),
        1.0,
        rtol=RTOL,
        atol=ATOL,
    )


def test_kim_model_matches_direct_evaluation():
    link = make_link(
        distance_m=1000.0,
        wavelength_nm=1550.0,
    )
    env = Environment(name="atmospheric")

    visibility_km = 2.0

    model = KimFogModel(
        link,
        env,
        visibility_km=visibility_km,
    )

    q = 0.16 * visibility_km + 0.34

    alpha_km = (
        (3.91 / visibility_km)
        * ((1550.0 / 550.0) ** (-q))
    )

    expected = np.exp(
        -(alpha_km / 1000.0) * link.range_m
    )

    np.testing.assert_allclose(
        model.gain(link, env),
        expected,
        rtol=RTOL,
        atol=ATOL,
    )


def test_lognormal_samples_have_unit_mean():
    link = make_link()
    env = Environment(name="atmospheric")

    model = LogNormalTurbulence(
        link,
        env,
        sigma_R2=0.1,
    )

    samples = model.sample(
        link,
        env,
        N,
        rng=SEED,
    )

    assert abs(np.mean(samples) - 1.0) < 0.02


def test_gamma_gamma_samples_have_unit_mean():
    link = make_link()
    env = Environment(name="atmospheric")

    model = GammaGammaTurbulence(
        link,
        env,
        gg_alpha=3.2,
        gg_beta=2.1,
    )

    samples = model.sample(
        link,
        env,
        N,
        rng=SEED,
    )

    assert abs(np.mean(samples) - 1.0) < 0.02


def test_pointing_sample_mean_matches_analytical_mean():
    link = make_link()
    env = Environment(name="atmospheric")

    model = RayleighGaussianPointingLoss(
        link,
        env,
        jitter_sigma_m=0.01,
        wz_eq_m=0.1,
    )

    expected = model.gain(link, env)

    samples = model.sample(
        link,
        env,
        N,
        rng=SEED,
    )

    assert abs(np.mean(samples) - expected) < 0.02
