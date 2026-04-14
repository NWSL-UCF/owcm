from .channel import Channel
from .core.registry import list_environments

# Register environments
from . import atmospheric
from . import indoor
from . import underwater
from . import underground
from . import space

__all__ = ["Channel", "list_environments"]
