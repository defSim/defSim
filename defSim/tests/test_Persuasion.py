from unittest import TestCase
from defSim.Simulation import Simulation


class TestPersuasion(TestCase):
    def test_spread_influence(self):
        simulation = Simulation(influence_function="persuasion",
                                max_iterations=100,
                                communication_regime="one-to-one")
        simulation.run()
