from typing import Any, Callable, Dict, Tuple, Optional, Set, List

# (env_name, category, model_name) -> ModelConstructor
ModelConstructor = Callable[..., Any] # Ideally returns a ChannelModel
MODEL_REGISTRY: Dict[Tuple[str, str, str], ModelConstructor] = {}

# env_name -> EnvSpec (placeholder for now, or just a set of valid names)
ENV_REGISTRY: Set[str] = set()

def register_model(env_name: str, category: str, model_name: str):
    """Decorator to register a model class."""
    def decorator(cls):
        MODEL_REGISTRY[(env_name, category, model_name)] = cls
        ENV_REGISTRY.add(env_name)
        # Store metadata on the class for easy retrieval
        if not hasattr(cls, '_owc_meta'):
             cls._owc_meta = {}
        cls._owc_meta.update({
            "env": env_name,
            "category": category,
            "name": model_name
        })
        return cls
    return decorator

def get_model(env_name: str, category: str, model_name: str) -> Optional[ModelConstructor]:
    return MODEL_REGISTRY.get((env_name, category, model_name))

def list_environments() -> List[str]:
    return sorted(list(ENV_REGISTRY))

def list_models(env_name: str) -> Dict[str, List[str]]:
    """Returns {category: [model_names]} for a given environment."""
    result = {}
    for (env, cat, name) in MODEL_REGISTRY.keys():
        if env == env_name:
            if cat not in result:
                result[cat] = []
            result[cat].append(name)
    return result
