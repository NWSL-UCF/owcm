from ..core.defaults import register_recipe

# Pure LoS only
register_recipe("indoor", "los", {
    "los": "lambertian_los",
    "nlos": "none",
    "blockage": "none"
})

# Room with LoS+NLoS (additive per Eq 37) and on-off blockage
register_recipe("indoor", "room_mvp", {
    "los": "lambertian_los_plus_nlos",
    "nlos": "none",
    "blockage": "onoff"
})

# LoS + NLoS + Markov blockage
register_recipe("indoor", "room_full", {
    "los": "lambertian_los_plus_nlos",
    "nlos": "none",
    "blockage": "markov"
})
