from ..core.defaults import register_recipe

register_recipe("underground", "mine_mvp", {
    "los": "lambertian_los",
    "dust": "exp_extinction",
    "blockage": "markov",
    "multipath": "none"
})
