from unittest import TestCase
from defSim import Experiment
from defSim.influence_sim import BoundedConfidence
from defSim.network_init import network_init
from defSim.agents_init import agents_init


class TestMultipleInfluenceFunctions(TestCase):

    def test_standard_influence_functions(self):

        experiment = Experiment(
            topology = 'grid' ,
            attributes_initializer = 'random_continuous',
            influence_function = 'list',
            network_parameters = {
                'influence_function': ['bounded_confidence', 'weighted_linear']
            }
            )

        print(experiment.run())