from unittest import TestCase
from defSim.agents_init import RandomCategoricalInitializer
from defSim.focal_agent_sim import RandomSelector
from defSim.neighbor_selector_sim import RandomNeighborSelector
from defSim.influence_sim import SimilarityAdoption
from defSim.dissimilarity_component import dissimilarity_calculator
from defSim.Simulation import Simulation

class TestSimulation(TestCase):
    def test_run_simulation(self):
        # test whether its possible to pass custom classes
        attribute_component = RandomCategoricalInitializer.RandomCategoricalInitializer()
        focal_agent_component = RandomSelector.RandomSelector()
        neighbor_component = RandomNeighborSelector.RandomNeighborSelector()
        influence_component = SimilarityAdoption.SimilarityAdoption()
        dissimilarity_measure = dissimilarity_calculator.select_calculator("hamming")
        simulation = Simulation(attributes_initializer=attribute_component,
                                focal_agent_selector=focal_agent_component,
                                neighbor_selector=neighbor_component,
                                influence_function=influence_component,
                                dissimilarity_measure=dissimilarity_measure,
                                communication_regime="one-to-many")
        pdf = simulation.run_simulation()
        print(pdf)