from unittest import TestCase
from defSim.Simulation import Simulation
from defSim.tools.ConvergenceChecks import OpinionDistanceConvergenceCheck

class TestConvergence(TestCase):
    simulation = Simulation(attributes_initializer="random_continuous",
                            influence_function="bounded_confidence",
                            dissimilarity_measure="euclidean",
                            communication_regime="one-to-many",
                            parameter_dict = {'confidence_bound': 0.5})

    def test_max_iterations(self):
        self.simulation.max_iterations = 10
        self.simulation.stop_condition = 'max_iteration'

        results = self.simulation.run()
        print(results)

    def test_pragmatic_convergence(self):
        self.simulation.max_iterations = 4000
        self.simulation.stop_condition = 'pragmatic_convergence'
        results = self.simulation.run()
        print(results)
        assert(results['Ticks'][0] < self.simulation.max_iterations)

    def test_opinion_distance_convergence(self):
        self.simulation.max_iterations = 4000
        self.simulation.stop_condition = 'strict_convergence'
        self.simulation.parameter_dict['threshold'] = 0.5
        results = self.simulation.run()
        print(results)
        assert(results['Ticks'][0] < self.simulation.max_iterations)

    def test_convergence_instance(self):
        self.simulation.max_iterations = 4000
        self.simulation.stop_condition = OpinionDistanceConvergenceCheck(maximum= 0.5)
        self.simulation.parameter_dict = {'confidence_bound': 0.5}
        results = self.simulation.run()
        print(results)
        assert(results['Ticks'][0] < self.simulation.max_iterations)                    

