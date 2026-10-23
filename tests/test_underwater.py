import numpy as np

from owcm.core.types import Link, Tx, Rx, Environment
from owcm.underwater.models.extinction import (
    UnderwaterExtinction,
)
from owcm.underwater.models.survey_model import (
    TableXILoS,
)

RTOL = 1e-6
ATOL = 1e-12


def make_link(
    distance_m=10.0,
    dr_m=0.1,
):
    tx = Tx(wavelength_nm=520.0)

    rx = Rx(
        aperture_diameter_m=dr_m
    )

    rx.position = np.array(
        [0.0, 0.0, distance_m]
    )

    return Link(tx=tx, rx=rx)


def test_underwater_extinction_matches_beer_lambert():
    link = make_link(
        distance_m=10.0
    )

    env = Environment(
        name="underwater",
        params={
            "attenuation_c": 0.1
        },
    )

    model = UnderwaterExtinction(
        link,
        env,
    )

    expected = np.exp(
        -0.1 * 10.0
    )

    np.testing.assert_allclose(
        model.gain(link, env),
        expected,
        rtol=RTOL,
        atol=ATOL,
    )


def test_underwater_extinction_uses_absorption_plus_scattering():
    link = make_link(
        distance_m=5.0
    )

    env = Environment(
        name="underwater",
        params={
            "attenuation_a": 0.03,
            "attenuation_b": 0.07,
        },
    )

    model = UnderwaterExtinction(
        link,
        env,
    )

    expected = np.exp(
        -(0.03 + 0.07) * 5.0
    )

    np.testing.assert_allclose(
        model.gain(link, env),
        expected,
        rtol=RTOL,
        atol=ATOL,
    )


def test_underwater_los_matches_direct_equation():
    link = make_link(
        distance_m=10.0,
        dr_m=0.1,
    )

    env = Environment(
        name="underwater"
    )

    theta = 0.0
    theta0 = 0.174
    c = 0.05
    eta_t = 0.9
    eta_r = 0.9

    model = TableXILoS(
        link,
        env,
        theta_rad=theta,
        theta0_rad=theta0,
        attenuation_c=c,
        etaT=eta_t,
        etaR=eta_r,
    )

    area = (
        np.pi
        * (0.1 / 2.0) ** 2
    )

    loss = np.exp(
        -c
        * link.range_m
        / np.cos(theta)
    )

    expected = (
        eta_t
        * eta_r
        * loss
        * area
        * np.cos(theta)
        / (
            2.0
            * np.pi
            * link.range_m**2
            * (
                1.0
                - np.cos(theta0)
            )
        )
    )

    np.testing.assert_allclose(
        model.gain(link, env),
        expected,
        rtol=RTOL,
        atol=ATOL,
    )
