from dataclasses import dataclass


@dataclass
class Plane:
    id: int
    airland_id: int
    A: int    # appearence time
    E: int    # earliest time
    T: int    # target time
    L: int    # latest time
    PCb: int  # cost per unit of time for arriving before target time
    PCa: int  # cost per unit of time for arriving after target time
    actual_land_time: int = 0
