from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


FIELD_SCHEMA = [
    {"group": "Scenario", "name": "settlement_name", "label": "Settlement Name", "type": "text", "help": "Used in the UI and reports."},
    {"group": "Scenario", "name": "seed", "label": "Random Seed", "type": "int", "min": 0, "max": 999999, "step": 1, "help": "The same seed reproduces the same event sequence."},
    {"group": "Scenario", "name": "target_turns", "label": "Victory Turns", "type": "int", "min": 6, "max": 120, "step": 1, "help": "Reach this turn with the settlement still stable to win."},
    {"group": "Population", "name": "initial_population", "label": "Starting Population", "type": "int", "min": 20, "max": 500, "step": 1, "help": "More people means more workers, but also higher demand."},
    {"group": "Population", "name": "starting_morale", "label": "Starting Morale", "type": "float", "min": 10, "max": 100, "step": 1, "help": "Affects productivity and unrest risk."},
    {"group": "Population", "name": "starting_health", "label": "Starting Health", "type": "float", "min": 10, "max": 100, "step": 1, "help": "Low health reduces workforce quality and increases deaths."},
    {"group": "Resources", "name": "starting_food", "label": "Starting Food", "type": "int", "min": 0, "max": 5000, "step": 5, "help": "Food is the main survival resource."},
    {"group": "Resources", "name": "starting_water", "label": "Starting Water", "type": "int", "min": 0, "max": 5000, "step": 5, "help": "Water shortages are especially dangerous."},
    {"group": "Resources", "name": "starting_energy", "label": "Starting Energy", "type": "int", "min": 0, "max": 5000, "step": 5, "help": "Energy supports housing, medicine, and production."},
    {"group": "Resources", "name": "starting_materials", "label": "Starting Materials", "type": "int", "min": 0, "max": 5000, "step": 5, "help": "Used to absorb shocks and build infrastructure."},
    {"group": "Infrastructure", "name": "farmland", "label": "Farmland", "type": "int", "min": 5, "max": 250, "step": 1, "help": "Determines food output."},
    {"group": "Infrastructure", "name": "water_infrastructure", "label": "Water Infrastructure", "type": "int", "min": 5, "max": 250, "step": 1, "help": "Determines water collection and purification."},
    {"group": "Infrastructure", "name": "generator_capacity", "label": "Generator Capacity", "type": "int", "min": 5, "max": 250, "step": 1, "help": "Determines weekly energy production."},
    {"group": "Infrastructure", "name": "medical_capacity", "label": "Medical Capacity", "type": "int", "min": 1, "max": 100, "step": 1, "help": "Reduces health losses and disease impact."},
    {"group": "Infrastructure", "name": "housing_capacity", "label": "Housing Capacity", "type": "int", "min": 10, "max": 700, "step": 1, "help": "Crowding lowers morale and health."},
    {"group": "World Conditions", "name": "climate_severity", "label": "Climate Severity", "type": "float", "min": 0, "max": 2, "step": 0.05, "help": "Harsh climates suppress food and water output."},
    {"group": "World Conditions", "name": "disease_risk", "label": "Disease Risk", "type": "float", "min": 0, "max": 1, "step": 0.05, "help": "Controls how likely disease events are to hit."},
    {"group": "World Conditions", "name": "trade_access", "label": "Trade Access", "type": "float", "min": 0, "max": 1, "step": 0.05, "help": "Improves material output and positive market events."},
    {"group": "World Conditions", "name": "hazard_frequency", "label": "Hazard Frequency", "type": "float", "min": 0, "max": 1, "step": 0.05, "help": "Higher values create more storms, unrest, and drought."},
    {"group": "World Conditions", "name": "research_rate", "label": "Research Rate", "type": "float", "min": 0.25, "max": 3, "step": 0.05, "help": "Improves knowledge gain and long-term efficiency."},
]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(slots=True)
class WorldConfig:
    settlement_name: str = "New Hearth"
    seed: int = 7
    target_turns: int = 24
    initial_population: int = 120
    starting_food: int = 420
    starting_water: int = 430
    starting_energy: int = 300
    starting_materials: int = 200
    starting_morale: float = 72.0
    starting_health: float = 76.0
    farmland: int = 48
    water_infrastructure: int = 42
    generator_capacity: int = 35
    medical_capacity: int = 12
    housing_capacity: int = 150
    climate_severity: float = 0.65
    disease_risk: float = 0.28
    trade_access: float = 0.5
    hazard_frequency: float = 0.35
    research_rate: float = 1.0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "WorldConfig":
        if not data:
            return cls()
        defaults = cls()
        clean: dict[str, Any] = {}
        for field in FIELD_SCHEMA:
            name = field["name"]
            raw = data.get(name, getattr(defaults, name))
            if field["type"] == "text":
                clean[name] = str(raw).strip() or "Unnamed Settlement"
            elif field["type"] == "int":
                clean[name] = int(round(_clamp(float(raw), field["min"], field["max"])))
            else:
                clean[name] = round(_clamp(float(raw), field["min"], field["max"]), 2)
        return cls(**clean)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
