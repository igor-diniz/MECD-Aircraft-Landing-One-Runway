from dataclasses import dataclass

@dataclass
class Plane:
    id: int
    airland_id: int
    appearance_time: float
    earliest_landing_time: float
    target_landing_time: float
    latest_landing_time: float
    pc_before_target: float
    pc_after_target: float