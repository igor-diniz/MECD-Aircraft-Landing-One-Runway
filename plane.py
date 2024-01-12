from dataclasses import dataclass


@dataclass
class Plane:
    id: int
    airland_id: int
    A: float    # appearence time
    E: float    # earliest time
    T: float    # target time
    L: float    # latest time
    PCb: float  # cost per unit of time for arriving before target time
    PCa: float  # cost per unit of time for arriving after target time
    actual_land_time: float = 0.0
