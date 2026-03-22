import unittest

from sim_game.config import WorldConfig
from sim_game.engine import SimulationEngine


class SimulationEngineTests(unittest.TestCase):
    def test_step_advances_turn_and_history(self) -> None:
        engine = SimulationEngine()
        state = engine.step("balanced")
        self.assertEqual(state["turn"], 1)
        self.assertEqual(len(state["history"]), 1)
        self.assertIn("statusText", state)

    def test_infrastructure_policy_builds_capacity(self) -> None:
        engine = SimulationEngine(
            WorldConfig(
                settlement_name="Builder Test",
                seed=3,
                target_turns=10,
                initial_population=80,
                starting_food=500,
                starting_water=500,
                starting_energy=500,
                starting_materials=500,
                starting_morale=80,
                starting_health=80,
                farmland=20,
                water_infrastructure=20,
                generator_capacity=20,
                medical_capacity=8,
                housing_capacity=90,
                climate_severity=0.3,
                disease_risk=0.1,
                trade_access=0.5,
                hazard_frequency=0.1,
                research_rate=1.0,
            )
        )
        before = engine.state.housing_capacity
        engine.step("infrastructure")
        self.assertGreater(engine.state.housing_capacity, before)

    def test_operation_changes_state_and_report(self) -> None:
        engine = SimulationEngine(
            WorldConfig(
                settlement_name="Ops Test",
                seed=5,
                target_turns=10,
                initial_population=80,
                starting_food=300,
                starting_water=300,
                starting_energy=300,
                starting_materials=300,
                starting_morale=70,
                starting_health=70,
                farmland=20,
                water_infrastructure=20,
                generator_capacity=20,
                medical_capacity=8,
                housing_capacity=90,
                climate_severity=0.3,
                disease_risk=0.1,
                trade_access=0.5,
                hazard_frequency=0.1,
                research_rate=1.0,
            )
        )
        before_water = engine.state.water
        state = engine.step("balanced", ["drill_wells"])
        self.assertGreater(state["water"], before_water - 10)
        self.assertIn("drill_wells", state["lastReport"]["operations"])

    def test_safe_world_can_reach_victory(self) -> None:
        engine = SimulationEngine(
            WorldConfig(
                settlement_name="Safe World",
                seed=1,
                target_turns=6,
                initial_population=60,
                starting_food=1200,
                starting_water=1200,
                starting_energy=900,
                starting_materials=400,
                starting_morale=85,
                starting_health=88,
                farmland=80,
                water_infrastructure=80,
                generator_capacity=60,
                medical_capacity=20,
                housing_capacity=90,
                climate_severity=0.1,
                disease_risk=0.0,
                trade_access=0.8,
                hazard_frequency=0.0,
                research_rate=1.2,
            )
        )
        state = engine.run(6, "balanced")
        self.assertEqual(state["outcome"], "victory")


if __name__ == "__main__":
    unittest.main()
