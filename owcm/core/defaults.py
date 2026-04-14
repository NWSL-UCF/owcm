import importlib
from typing import Dict, Any

# env_name -> {recipe_name: {category: model_name}}
_RECIPES: Dict[str, Dict[str, Dict[str, str]]] = {}

def load_environment_recipes(env_name: str):
    """
    Dynamically attempts to import owc.{env_name}.recipes.
    This ensures models are registered and recipes are loaded.
    """
    try:
        # Import the module. This should execute code that populates _RECIPES
        # or at least ensures the sub-package is loaded.
        importlib.import_module(f"owcm.{env_name}.recipes")
    except ImportError:
        pass # It's possible the environment doesn't have recipes yet

def register_recipe(env_name: str, recipe_name: str, config: Dict[str, str]):
    if env_name not in _RECIPES:
        _RECIPES[env_name] = {}
    _RECIPES[env_name][recipe_name] = config

def get_recipe(env_name: str, recipe_name: str) -> Dict[str, str]:
    # Ensure recipes are loaded
    if env_name not in _RECIPES:
        load_environment_recipes(env_name)
    
    env_recipes = _RECIPES.get(env_name, {})
    if recipe_name not in env_recipes:
        raise ValueError(f"Recipe '{recipe_name}' not found for environment '{env_name}'. Available: {list(env_recipes.keys())}")
    return env_recipes[recipe_name]
