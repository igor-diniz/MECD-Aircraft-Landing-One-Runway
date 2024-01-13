from dataclasses import dataclass


@dataclass
class Plane:
    id: int
    airland_id: int
    A: float  # Appearance time
    E: float  # Earliest landing time
    T: float  # Target landing time
    L: float  # Latest landing time
    PCb: float  # Penalty cost per unit of time for landing before target
    PCa: float  # Penalty cost per unit of time for landing after target
    landing_time: float = 0.0