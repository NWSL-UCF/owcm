from typing import List, Optional, Union, Dict, Any
import numpy as np
from .types import ChannelModel, Link, Environment

class CompositeChannel:
    """
    A composite channel that multiplies the gains of multiple sub-models.
    Implements the ChannelModel protocol.
    
    h_total = product(h_i) represents independent multiplicative loss/fading mechanisms.
    """
    def __init__(self, models: List[ChannelModel]):
        self.models = models

    def gain(self, link: Link, env: Environment, rng: Optional[np.random.Generator] = None) -> Union[float, np.ndarray]:
        total_gain = 1.0
        for model in self.models:
            total_gain *= model.gain(link, env, rng=rng)
        return total_gain

    def sample(self, link: Link, env: Environment, n: int, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        # Note: This assumes independence between channel components for sampling
        total_samples = np.ones(n)
        for model in self.models:
            total_samples *= model.sample(link, env, n, rng=rng)
        return total_samples

    def describe(self) -> Dict[str, Any]:
        return {
            "type": "CompositeChannel",
            "components": [m.describe() for m in self.models]
        }
