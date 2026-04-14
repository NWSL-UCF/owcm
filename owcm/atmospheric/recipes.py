from ..core.defaults import register_recipe

register_recipe("atmospheric", "mvp", {
    "geometry": "uniform_aperture",
    "attenuation": "kim",
    "turbulence": "gamma_gamma",
    "pointing": "rayleigh_gaussian"
})

register_recipe("atmospheric", "clear_air", {
    "geometry": "uniform_aperture",
    "attenuation": "beer_lambert", 
    "turbulence": "lognormal",
    "pointing": "none"
})

register_recipe("atmospheric", "dense_fog", {
    "geometry": "gaussian_collected_approx",
    "attenuation": "kim", 
    "turbulence": "gamma_gamma",
    "pointing": "rayleigh_gaussian"
})
