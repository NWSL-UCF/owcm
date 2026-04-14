from ..core.defaults import register_recipe

register_recipe("space", "deep_space", {
    "free_space": "fspl",
    "tx_gain": "diffraction_limited",
    "rx_gain": "telescope",
    "pointing": "none",
    "atmospheric_entry": "none",
    "link_budget": "multiplicative_chain"
})
