from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, Union
import numpy as np

@dataclass
class Environment:
    """Base class for all OWC environments."""
    name: str = "Generic Environment"
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Tx:
    """Transmitter parameters."""
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    power_dbm: float = 0.0  # Transmit power in dBm
    wavelength_nm: float = 1550.0 # Wavelength in nm
    divergence_angle_rad: float = 0.0 # Beam divergence half-angle
    aperture_diameter_m: float = 0.05

@dataclass
class Rx:
    """Receiver parameters."""
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 1000.0]))
    aperture_diameter_m: float = 0.1
    field_of_view_rad: float = np.pi / 2 # Half-angle FOV
    sensitivity_dbm: float = -30.0

@dataclass
class Link:
    """Geometric link configuration."""
    tx: Tx
    rx: Rx
    range_m: float = field(init=False)

    def __post_init__(self):
        self.range_m = np.linalg.norm(self.rx.position - self.tx.position)

@dataclass
class Results:
    """Container for simulation results."""
    h_channel: Union[float, np.ndarray]
    received_power_watts: Union[float, np.ndarray]
    snr_db: Optional[Union[float, np.ndarray]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ChannelModel(Protocol):
    """Protocol for all channel models."""
    
    def gain(self, link: Link, env: Environment, rng: Optional[np.random.Generator] = None) -> Union[float, np.ndarray]:
        """Calculate the channel gain (linear scale)."""
        ...

    def sample(self, link: Link, env: Environment, n: int, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        """Draw n samples from the channel distribution."""
        ...

    def describe(self) -> Dict[str, Any]:
        """Return model metadata, equation references, and parameters."""
        ...
