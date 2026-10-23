import numpy as np

from owcm.core.types import Link, Tx, Rx, Environment
from owcm.underground.models.all_models import (
    UndergroundLoS,
    DustExtinction,
    OnOffBlockage,
)

RTOL = 1e-6
ATOL = 1e-12
N = 100000
SEED = 42


def make_link(distance_m=20.0):
    tx = Tx(wavelength_nm=850.0)

    rx = Rx()

    rx.position = np.array(
        [0.0, 0.0, distance_m]
    )

    return Link(tx=tx, rx=rx)


def test_underground_los_inverse_square_scaling():
    env = Environment(
        name="underground"
    )

    link1 = make_link(10.0)
    link2 = make_link(20.0)

    model1 = UndergroundLoS(
        link1,
        env,
    )

    model2 = UndergroundLoS(
        link2,
        env,
    )

    ratio = (
        model1.gain(link1, env)
        / model2.gain(link2, env)
    )

    assert abs(
        ratio - 4.0
    ) < 0.4


def test_dust_extinction_matches_closed_form():
    link = make_link(20.0)

    env = Environment(
        name="underground"
    )

    concentration = 0.01
    k = 0.5

    model = DustExtinction(
        link,
        env,
        dust_conc_mg_m3=concentration,
        dust_k_per_m_per_mg_m3=k,
    )

    expected = np.exp(
        -k
        * concentration
        * link.range_m
    )

    np.testing.assert_allclose(
        model.gain(link, env),
        expected,
        rtol=RTOL,
        atol=ATOL,
    )


def test_zero_dust_has_unity_gain():
    link = make_link()

    env = Environment(
        name="underground"
    )

    model = DustExtinction(
        link,
        env,
        dust_conc_mg_m3=0.0,
    )

    np.testing.assert_allclose(
        model.gain(link, env),
        1.0,
        rtol=RTOL,
        atol=ATOL,
    )


def test_underground_onoff_mean_matches_probability():
    link = make_link()

    env = Environment(
        name="underground"
    )

    p_blocked = 0.4

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
