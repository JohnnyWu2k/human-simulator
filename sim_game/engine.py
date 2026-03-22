from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from sim_game.config import WorldConfig


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _rounded(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in data.items():
        result[key] = round(value, 2) if isinstance(value, float) else value
    return result


def _build_judgement(state: "SimulationState") -> dict[str, Any]:
    alerts: list[str] = []
    resource_turns = {
        "food": state.food / max(1.0, state.population * 0.94),
        "water": state.water / max(1.0, state.population * 1.08),
        "energy": state.energy / max(1.0, state.population * 0.46),
    }
    if resource_turns["food"] < 1.5:
        alerts.append("Food will run out very soon.")
    if resource_turns["water"] < 1.5:
        alerts.append("Water is at immediate collapse risk.")
    if state.health < 35:
        alerts.append("Health is in a lethal zone.")
    if state.morale < 35:
        alerts.append("Morale is low enough to suppress output.")
    if state.population > state.housing_capacity:
        alerts.append("Housing is overcrowded.")
    if state.turn >= state.target_turns:
        alerts.append("Target horizon reached.")

    level = "stable"
    if state.outcome == "victory":
        level = "victory"
    elif state.outcome == "defeat":
        level = "defeat"
    elif alerts:
        level = "critical" if any("immediate" in item or "lethal" in item for item in alerts) else "warning"

    return {
        "level": level,
        "resourceTurns": _rounded(resource_turns),
        "alerts": alerts,
    }


@dataclass(frozen=True, slots=True)
class Policy:
    name: str
    label: str
    description: str
    food_mult: float = 1.0
    water_mult: float = 1.0
    energy_mult: float = 1.0
    materials_mult: float = 1.0
    consumption_mult: float = 1.0
    research_mult: float = 1.0
    morale_delta: float = 0.0
    health_delta: float = 0.0
    disease_guard: float = 1.0


@dataclass(frozen=True, slots=True)
class Operation:
    name: str
    label: str
    description: str
    effects: str


@dataclass(frozen=True, slots=True)
class OperationStatus:
    name: str
    can_execute: bool
    reason: str


POLICIES = {
    "balanced": Policy("balanced", "Balanced", "Steady output with no major bias."),
    "agriculture": Policy("agriculture", "Agriculture Push", "Prioritize farms and waterworks for survival output.", food_mult=1.45, water_mult=1.1, materials_mult=0.82, research_mult=0.85, morale_delta=-1.0),
    "industry": Policy("industry", "Industry Drive", "Push materials and power production at the cost of comfort.", food_mult=0.85, energy_mult=1.15, materials_mult=1.55, research_mult=0.9, morale_delta=-2.5),
    "welfare": Policy("welfare", "Welfare Program", "Stabilize health and morale while sacrificing some output.", materials_mult=0.8, research_mult=0.85, morale_delta=4.5, health_delta=3.5),
    "research": Policy("research", "Research Sprint", "Invest effort into knowledge and efficiency gains.", food_mult=0.92, materials_mult=0.9, research_mult=1.9, morale_delta=-1.5),
    "rationing": Policy("rationing", "Rationing", "Stretch resources through reduced consumption and discipline.", consumption_mult=0.8, morale_delta=-4.5, health_delta=-1.5),
    "quarantine": Policy("quarantine", "Quarantine", "Suppress disease spread, but hamper trade and morale.", materials_mult=0.78, morale_delta=-3.5, disease_guard=0.45),
    "infrastructure": Policy("infrastructure", "Infrastructure Build", "Spend materials to expand capacity and long-term resilience.", food_mult=0.88, materials_mult=0.7, research_mult=0.9, morale_delta=-1.0),
}

OPERATIONS = {
    "emergency_rations": Operation("emergency_rations", "Emergency Rations", "Spend reserves to calm unrest and stabilize public health.", "Costs food and materials. Raises morale and health."),
    "repair_grid": Operation("repair_grid", "Repair Grid", "Dispatch engineers to restore local utilities.", "Costs materials. Grants a burst of energy and small morale recovery."),
    "medical_outreach": Operation("medical_outreach", "Medical Outreach", "Send treatment crews into the settlement.", "Costs materials and energy. Raises health and morale."),
    "trade_convoy": Operation("trade_convoy", "Trade Convoy", "Send a caravan to convert supplies into imported goods.", "Costs food and water. Gains materials with some uncertainty."),
    "drill_wells": Operation("drill_wells", "Drill Wells", "Invest in emergency extraction and purification.", "Costs materials and energy. Gains water and some knowledge."),
    "festival": Operation("festival", "Festival", "Organize a celebration to pull people out of fear.", "Costs food and energy. Strong morale boost."),
    "survey_expedition": Operation("survey_expedition", "Survey Expedition", "Scout nearby zones for future opportunities.", "Costs materials and energy. Gains knowledge with risk-sensitive bonuses."),
    "housing_drive": Operation("housing_drive", "Housing Drive", "Convert stockpiles into rapid shelter expansion.", "Costs materials and energy. Increases housing capacity."),
}


@dataclass(slots=True)
class SimulationState:
    settlement_name: str
    seed: int
    target_turns: int
    turn: int
    population: int
    food: float
    water: float
    energy: float
    materials: float
    morale: float
    health: float
    knowledge: float
    farmland: int
    water_infrastructure: int
    generator_capacity: int
    medical_capacity: int
    housing_capacity: int
    outcome: str = "ongoing"
    history: list[dict[str, Any]] = field(default_factory=list)
    last_report: dict[str, Any] | None = None

    @property
    def turns_remaining(self) -> int:
        return max(0, self.target_turns - self.turn)

    @property
    def status_text(self) -> str:
        if self.outcome == "victory":
            return "Victory. The settlement reached its horizon in stable condition."
        if self.outcome == "defeat":
            return "Collapse. The settlement can no longer sustain itself."
        if self.morale < 30 or self.health < 30:
            return "Fragile. Immediate stabilization is needed."
        if self.food < self.population * 2 or self.water < self.population * 2:
            return "Strained. Resource shortages are approaching."
        return "Stable. The colony is holding together."

    def to_dict(self) -> dict[str, Any]:
        return _rounded(
            {
                "settlementName": self.settlement_name,
                "seed": self.seed,
                "targetTurns": self.target_turns,
                "turn": self.turn,
                "population": self.population,
                "food": self.food,
                "water": self.water,
                "energy": self.energy,
                "materials": self.materials,
                "morale": self.morale,
                "health": self.health,
                "knowledge": self.knowledge,
                "farmland": self.farmland,
                "waterInfrastructure": self.water_infrastructure,
                "generatorCapacity": self.generator_capacity,
                "medicalCapacity": self.medical_capacity,
                "housingCapacity": self.housing_capacity,
                "outcome": self.outcome,
                "turnsRemaining": self.turns_remaining,
                "history": self.history,
                "lastReport": self.last_report,
                "judgement": _build_judgement(self),
                "operationStatuses": [],
                "statusText": self.status_text,
            }
        )


class SimulationEngine:
    def __init__(self, config: WorldConfig | None = None) -> None:
        self.config = config or WorldConfig()
        self.random = random.Random(self.config.seed)
        self.state = self._build_state(self.config)

    def reset(self, config: WorldConfig | None = None) -> dict[str, Any]:
        self.config = config or WorldConfig()
        self.random = random.Random(self.config.seed)
        self.state = self._build_state(self.config)
        return self.serialize_state()

    def step(self, policy_name: str, operations: list[str] | None = None) -> dict[str, Any]:
        if self.state.outcome != "ongoing":
            return self.serialize_state()

        policy = POLICIES.get(policy_name, POLICIES["balanced"])
        state = self.state
        operation_notes, executed_operations = self._apply_operations(operations or [])

        climate_factor = max(0.35, 1.08 - (self.config.climate_severity * 0.24) + self.random.uniform(-0.08, 0.06))
        workforce_ratio = max(0.35, (state.health / 100.0) * 0.58 + (state.morale / 100.0) * 0.32)
        workforce = state.population * workforce_ratio
        knowledge_bonus = 1.0 + (state.knowledge / 200.0)

        production = {
            "food": state.farmland * 1.58 * climate_factor * policy.food_mult * knowledge_bonus,
            "water": state.water_infrastructure * 1.46 * max(0.45, 1.06 - self.config.climate_severity * 0.15) * policy.water_mult,
            "energy": state.generator_capacity * 1.52 * policy.energy_mult,
            "materials": workforce * 0.17 * policy.materials_mult * (0.78 + self.config.trade_access * 0.48),
        }
        consumption = {
            "food": state.population * 0.94 * policy.consumption_mult,
            "water": state.population * 1.08 * policy.consumption_mult,
            "energy": state.population * 0.46 + state.housing_capacity * 0.03,
        }
        research_gain = workforce / 22.0 * policy.research_mult * self.config.research_rate * (0.65 + state.morale / 180.0)

        state.food += production["food"] - consumption["food"]
        state.water += production["water"] - consumption["water"]
        state.energy += production["energy"] - consumption["energy"]
        state.materials += production["materials"]
        state.knowledge += research_gain
        state.morale = _clamp(state.morale + policy.morale_delta, 0.0, 100.0)
        state.health = _clamp(state.health + policy.health_delta, 0.0, 100.0)

        events, notes = self._apply_events(policy)
        notes = operation_notes + notes

        infrastructure_note = self._apply_infrastructure(policy)
        if infrastructure_note:
            notes.append(infrastructure_note)

        shortage_notes, deaths = self._resolve_shortages(consumption)
        notes.extend(shortage_notes)

        overflow = max(0, state.population - state.housing_capacity)
        if overflow:
            crowding_ratio = overflow / max(1, state.population)
            state.morale = _clamp(state.morale - crowding_ratio * 12.0, 0.0, 100.0)
            state.health = _clamp(state.health - crowding_ratio * 7.0, 0.0, 100.0)
            notes.append("Crowded housing reduced morale and health.")

        state.health = _clamp(state.health + min(4.0, state.medical_capacity / max(1, state.population) * 42.0), 0.0, 100.0)

        births = 0
        if state.food > state.population * 2.2 and state.water > state.population * 2.3 and state.morale > 62 and state.health > 60:
            births = max(0, int(state.population * (0.003 + state.knowledge / 8000.0)))
        natural_losses = int(state.population * max(0.0, 0.012 - (state.health / 100.0) * 0.007 - (state.morale / 100.0) * 0.003))
        state.population = max(0, state.population + births - deaths - natural_losses)
        if births:
            notes.append(f"{births} new settlers joined the population.")
        if natural_losses:
            notes.append(f"{natural_losses} settlers were lost to ordinary attrition.")

        state.turn += 1
        self._update_outcome()
        state.last_report = {
            "turn": state.turn,
            "policyName": policy.name,
            "policy": policy.label,
            "operations": executed_operations,
            "events": events,
            "notes": notes,
            "production": _rounded(production),
            "consumption": _rounded(consumption),
            "populationDelta": births - deaths - natural_losses,
            "status": state.status_text,
        }
        state.history.append(
            _rounded(
                {
                    "turn": state.turn,
                    "population": state.population,
                    "food": state.food,
                    "water": state.water,
                    "energy": state.energy,
                    "materials": state.materials,
                    "morale": state.morale,
                    "health": state.health,
                    "knowledge": state.knowledge,
                    "policy": policy.name,
                    "operations": executed_operations,
                    "events": events,
                    "outcome": state.outcome,
                }
            )
        )
        return self.serialize_state()

    def run(
        self,
        turns: int,
        default_policy: str,
        schedule: list[str] | None = None,
        operations: list[str] | None = None,
    ) -> dict[str, Any]:
        plan = schedule or []
        repeating_operations = operations or []
        for index in range(max(0, turns)):
            policy_name = plan[index] if index < len(plan) else default_policy
            self.step(policy_name, repeating_operations)
            if self.state.outcome != "ongoing":
                break
        return self.serialize_state()

    def available_policies(self) -> list[dict[str, str]]:
        return [{"name": item.name, "label": item.label, "description": item.description} for item in POLICIES.values()]

    def available_operations(self) -> list[dict[str, str]]:
        return [
            {
                "name": item.name,
                "label": item.label,
                "description": item.description,
                "effects": item.effects,
            }
            for item in OPERATIONS.values()
        ]

    def serialize_state(self) -> dict[str, Any]:
        data = self.state.to_dict()
        data["operationStatuses"] = self.operation_statuses()
        return data

    def operation_statuses(self) -> list[dict[str, Any]]:
        return [
            {
                "name": status.name,
                "canExecute": status.can_execute,
                "reason": status.reason,
            }
            for status in self._operation_statuses()
        ]

    def _build_state(self, config: WorldConfig) -> SimulationState:
        return SimulationState(
            settlement_name=config.settlement_name,
            seed=config.seed,
            target_turns=config.target_turns,
            turn=0,
            population=config.initial_population,
            food=float(config.starting_food),
            water=float(config.starting_water),
            energy=float(config.starting_energy),
            materials=float(config.starting_materials),
            morale=float(config.starting_morale),
            health=float(config.starting_health),
            knowledge=0.0,
            farmland=config.farmland,
            water_infrastructure=config.water_infrastructure,
            generator_capacity=config.generator_capacity,
            medical_capacity=config.medical_capacity,
            housing_capacity=config.housing_capacity,
        )

    def _operation_statuses(self) -> list[OperationStatus]:
        state = self.state
        checks = {
            "emergency_rations": (state.food >= 20 and state.materials >= 8, "Needs 20 food and 8 materials."),
            "repair_grid": (state.materials >= 16, "Needs 16 materials."),
            "medical_outreach": (state.materials >= 18 and state.energy >= 10, "Needs 18 materials and 10 energy."),
            "trade_convoy": (state.food >= 18 and state.water >= 18, "Needs 18 food and 18 water."),
            "drill_wells": (state.materials >= 20 and state.energy >= 12, "Needs 20 materials and 12 energy."),
            "festival": (state.food >= 24 and state.energy >= 12, "Needs 24 food and 12 energy."),
            "survey_expedition": (state.materials >= 8 and state.energy >= 14, "Needs 8 materials and 14 energy."),
            "housing_drive": (state.materials >= 28 and state.energy >= 6, "Needs 28 materials and 6 energy."),
        }
        statuses: list[OperationStatus] = []
        for name in OPERATIONS:
            ok, reason = checks[name]
            statuses.append(OperationStatus(name=name, can_execute=ok, reason=("Ready." if ok else reason)))
        return statuses

    def _apply_operations(self, operations: list[str]) -> tuple[list[str], list[str]]:
        state = self.state
        notes: list[str] = []
        executed: list[str] = []
        seen: set[str] = set()

        for name in operations[:2]:
            if name not in OPERATIONS or name in seen:
                continue
            seen.add(name)

            if name == "emergency_rations":
                if state.food < 20 or state.materials < 8:
                    notes.append("Emergency Rations could not be executed due to insufficient food or materials.")
                    continue
                state.food -= 20
                state.materials -= 8
                state.morale = _clamp(state.morale + 6.0, 0.0, 100.0)
                state.health = _clamp(state.health + 3.0, 0.0, 100.0)
                notes.append("Emergency Rations spent 20 food and 8 materials to calm the settlement.")
            elif name == "repair_grid":
                if state.materials < 16:
                    notes.append("Repair Grid could not be executed due to insufficient materials.")
                    continue
                state.materials -= 16
                state.energy += 50
                state.morale = _clamp(state.morale + 1.0, 0.0, 100.0)
                notes.append("Repair Grid restored 50 energy at a cost of 16 materials.")
            elif name == "medical_outreach":
                if state.materials < 18 or state.energy < 10:
                    notes.append("Medical Outreach could not be executed due to insufficient materials or energy.")
                    continue
                state.materials -= 18
                state.energy -= 10
                state.health = _clamp(state.health + 8.0, 0.0, 100.0)
                state.morale = _clamp(state.morale + 2.0, 0.0, 100.0)
                notes.append("Medical Outreach spent 18 materials and 10 energy to improve health and morale.")
            elif name == "trade_convoy":
                if state.food < 18 or state.water < 18:
                    notes.append("Trade Convoy could not be executed due to insufficient food or water.")
                    continue
                state.food -= 18
                state.water -= 18
                materials_gain = 24 + self.random.randint(0, 18) + int(self.config.trade_access * 12)
                state.materials += materials_gain
                notes.append(f"Trade Convoy converted supplies into {materials_gain} imported materials.")
            elif name == "drill_wells":
                if state.materials < 20 or state.energy < 12:
                    notes.append("Drill Wells could not be executed due to insufficient materials or energy.")
                    continue
                state.materials -= 20
                state.energy -= 12
                state.water += 60
                state.knowledge += 2
                notes.append("Drill Wells added 60 water and 2 knowledge at the cost of materials and energy.")
            elif name == "festival":
                if state.food < 24 or state.energy < 12:
                    notes.append("Festival could not be executed due to insufficient food or energy.")
                    continue
                state.food -= 24
                state.energy -= 12
                state.morale = _clamp(state.morale + 9.0, 0.0, 100.0)
                notes.append("Festival lifted morale by spending 24 food and 12 energy.")
            elif name == "survey_expedition":
                if state.materials < 8 or state.energy < 14:
                    notes.append("Survey Expedition could not be executed due to insufficient materials or energy.")
                    continue
                state.materials -= 8
                state.energy -= 14
                knowledge_gain = 6 + self.random.randint(0, 4)
                state.knowledge += knowledge_gain
                if self.random.random() > self.config.hazard_frequency:
                    bonus = 8 + self.random.randint(0, 12)
                    state.materials += bonus
                    notes.append(f"Survey Expedition gained {knowledge_gain} knowledge and discovered {bonus} materials.")
                else:
                    morale_loss = 2 + self.random.randint(0, 2)
                    state.morale = _clamp(state.morale - morale_loss, 0.0, 100.0)
                    notes.append(f"Survey Expedition gained {knowledge_gain} knowledge but hurt morale by {morale_loss}.")
            elif name == "housing_drive":
                if state.materials < 28 or state.energy < 6:
                    notes.append("Housing Drive could not be executed due to insufficient materials or energy.")
                    continue
                state.materials -= 28
                state.energy -= 6
                state.housing_capacity += 10
                state.morale = _clamp(state.morale + 2.0, 0.0, 100.0)
                notes.append("Housing Drive increased housing capacity by 10.")

            executed.append(name)

        return notes, executed

    def _apply_events(self, policy: Policy) -> tuple[list[str], list[str]]:
        state = self.state
        events: list[str] = []
        notes: list[str] = []

        if self.random.random() < 0.18 + self.config.hazard_frequency * 0.5:
            pressure = self.random.random()
            if pressure < self.config.climate_severity / 2.2:
                loss = 18 + self.random.randint(6, 35)
                state.water = max(0.0, state.water - loss)
                state.morale = _clamp(state.morale - 3.0, 0.0, 100.0)
                events.append("Drought")
                notes.append(f"A drought consumed {loss} water reserves.")
            elif pressure < self.config.climate_severity / 1.5:
                energy_loss = 12 + self.random.randint(8, 22)
                materials_loss = 5 + self.random.randint(4, 16)
                state.energy = max(0.0, state.energy - energy_loss)
                state.materials = max(0.0, state.materials - materials_loss)
                state.morale = _clamp(state.morale - 4.0, 0.0, 100.0)
                events.append("Storm Damage")
                notes.append(f"Storms destroyed {energy_loss} energy and {materials_loss} materials.")
            elif pressure < self.config.climate_severity / 1.2 + self.config.disease_risk / 2:
                severity = (6 + self.random.randint(0, 8)) * policy.disease_guard
                population_loss = int(max(0.0, severity / 3.5 - state.medical_capacity / 12.0))
                state.health = _clamp(state.health - severity, 0.0, 100.0)
                state.population = max(0, state.population - population_loss)
                events.append("Disease Outbreak")
                notes.append(f"Infections reduced health by {severity:.1f} and cost {population_loss} settlers.")
            else:
                morale_loss = 5 + self.random.randint(1, 7)
                materials_loss = 4 + self.random.randint(1, 10)
                state.morale = _clamp(state.morale - morale_loss, 0.0, 100.0)
                state.materials = max(0.0, state.materials - materials_loss)
                events.append("Civil Dispute")
                notes.append(f"Internal conflict cut morale by {morale_loss} and wasted {materials_loss} materials.")

        if self.random.random() < 0.16 + self.config.trade_access * 0.18 + self.config.research_rate * 0.06:
            opportunity = self.random.random()
            if opportunity < self.config.trade_access:
                materials_gain = 14 + self.random.randint(8, 26)
                food_gain = 10 + self.random.randint(5, 18)
                state.materials += materials_gain
                state.food += food_gain
                events.append("Market Windfall")
                notes.append(f"Trading caravans added {materials_gain} materials and {food_gain} food.")
            elif opportunity < 0.6:
                food_gain = 24 + self.random.randint(10, 36)
                state.food += food_gain
                state.morale = _clamp(state.morale + 3.0, 0.0, 100.0)
                events.append("Bountiful Harvest")
                notes.append(f"An exceptional harvest brought in {food_gain} food.")
            elif opportunity < 0.82:
                knowledge_gain = 4 + self.random.randint(2, 8)
                state.knowledge += knowledge_gain
                state.morale = _clamp(state.morale + 2.0, 0.0, 100.0)
                events.append("Research Breakthrough")
                notes.append(f"Researchers added {knowledge_gain} knowledge.")
            else:
                settlers = 4 + self.random.randint(2, 10)
                state.population += settlers
                state.food = max(0.0, state.food - settlers * 1.2)
                state.morale = _clamp(state.morale + (2.0 if state.population <= state.housing_capacity else -2.0), 0.0, 100.0)
                events.append("Migrant Arrival")
                notes.append(f"{settlers} migrants joined the settlement.")

        return events, notes

    def _apply_infrastructure(self, policy: Policy) -> str | None:
        if policy.name != "infrastructure":
            return None
        if self.state.materials < 35:
            return "Infrastructure teams lacked the 35 materials needed to expand capacity."
        self.state.materials -= 35
        self.state.farmland += 2
        self.state.water_infrastructure += 1
        self.state.generator_capacity += 1
        self.state.medical_capacity += 1
        self.state.housing_capacity += 6
        return "Builders spent 35 materials to expand farms, utilities, medicine, and housing."

    def _resolve_shortages(self, consumption: dict[str, float]) -> tuple[list[str], int]:
        state = self.state
        notes: list[str] = []
        deaths = 0

        food_deficit = max(0.0, -state.food)
        if food_deficit:
            state.food = 0.0
            ratio = min(1.0, food_deficit / max(1.0, consumption["food"]))
            state.health = _clamp(state.health - ratio * 18.0, 0.0, 100.0)
            state.morale = _clamp(state.morale - ratio * 15.0, 0.0, 100.0)
            starvation = int(state.population * ratio * 0.04)
            deaths += starvation
            notes.append(f"Food shortage caused {starvation} starvation deaths.")

        water_deficit = max(0.0, -state.water)
        if water_deficit:
            state.water = 0.0
            ratio = min(1.0, water_deficit / max(1.0, consumption["water"]))
            state.health = _clamp(state.health - ratio * 24.0, 0.0, 100.0)
            state.morale = _clamp(state.morale - ratio * 10.0, 0.0, 100.0)
            dehydration = int(state.population * ratio * 0.05)
            deaths += dehydration
            notes.append(f"Water shortage caused {dehydration} dehydration deaths.")

        energy_deficit = max(0.0, -state.energy)
        if energy_deficit:
            state.energy = 0.0
            ratio = min(1.0, energy_deficit / max(1.0, consumption["energy"]))
            state.health = _clamp(state.health - ratio * 6.0, 0.0, 100.0)
            state.morale = _clamp(state.morale - ratio * 12.0, 0.0, 100.0)
            notes.append("Energy shortages disrupted daily life and healthcare.")

        return notes, deaths

    def _update_outcome(self) -> None:
        state = self.state
        if state.population <= 0 or state.health <= 0 or state.morale <= 0:
            state.outcome = "defeat"
        elif state.turn >= state.target_turns and state.health > 15 and state.morale > 15:
            state.outcome = "victory"
        else:
            state.outcome = "ongoing"
