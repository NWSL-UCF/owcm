from ..core.defaults import register_recipe

# Simple Beer–Lambert extinction only (no explicit link geometry)
register_recipe("underwater", "beer_lambert", {
    "extinction": "a_plus_b",
    "scattering": "none",
    "pointing": "none",
})

# Analytical LoS link from survey Table XI (Eq. 48).
# Uses category "link" -> "los_case" implemented in survey_model.TableXILoS.
register_recipe("underwater", "los_link", {
    "link": "los_case",
})

# Modulating retroreflector link from survey Table XI (Eq. 49).
register_recipe("underwater", "retro_link", {
    "link": "retroreflective_case",
})

# Reflective NLoS link using water–air interface (Eq. 50–51).
register_recipe("underwater", "reflective_link", {
    "nlos": "reflective_case",
})
