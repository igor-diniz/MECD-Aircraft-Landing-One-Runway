from dataclasses import dataclass


@dataclass
class Plane:
    id: int
    airland_id: int
    A: float
    E: float
    T: float
    L: float
    PCb: float
    PCa: float
    landing_time: float = 0.0