from unittest import TestCase
from defSim.network_init import network_init
from defSim.agents_init import agents_init


class TestAgentInit(TestCase):

    def test_random_continuous(self):
        network1 = network_init.generate_network("grid", **{"num_agents": 4})
        # default values
        agents_init.initialize_attributes(network1, "random_continuous")
        # more features
        agents_init.initialize_attributes(network1, "random_continuous", **{"num_features": 3})
        # non-implemented distribution
        with self.assertRaises(NotImplementedError):
            agents_init.initialize_attributes(network1, "random_continuous", **{"distribution": "notimplemented", "num_features": 1})

    def test_correlated_continuous(self):
        network1 = network_init.generate_network("grid", **{"num_agents": 300})
        # default values
        agents_init.initialize_attributes(network1, "correlated_continuous")
        # more features
        agents_init.initialize_attributes(network1, "correlated_continuous", **{'num_features': 3})
        # non-implemented distribution
        with self.assertRaises(NotImplementedError):
            agents_init.initialize_attributes(network1, "correlated_continuous", **{"distribution": "notimplemented", "num_features": 3})        

