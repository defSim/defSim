from unittest import TestCase
from defSim import Experiment
from defSim.influence_sim import BoundedConfidence
from defSim.network_init import network_init
from defSim.agents_init import agents_init


class TestNetworkList(TestCase):

    def test_network_list(self):
        network1 = network_init.generate_network("grid")
        network2 = network_init.generate_network("ring")

        experiment = Experiment(
            network = 'list',
            attributes_initializer = 'random_continuous',
            influence_function = 'bounded_confidence',
            network_parameters = {
                'network': [network1, network2]
            }
            )

        print(experiment.run())