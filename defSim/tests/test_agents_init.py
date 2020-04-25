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

    def test_networkcorrelated_continuous(self):
        network1 = network_init.generate_network("grid", **{"num_agents": 50})
        # default values
        agents_init.initialize_attributes(network1, "network_correlated_continuous")
        # more features and set correlation
        agents_init.initialize_attributes(network1, "network_correlated_continuous", **{'num_features': 3, 'correlation': 0.6})
        # correctly specified covariance matrix
        agents_init.initialize_attributes(network1, "network_correlated_continuous", **{'num_features': 2, 'covariances': [[1, 0.4],[0.4, 1]]})  
        # poorly specified covariance matrix
        with self.assertWarns(RuntimeWarning):
            agents_init.initialize_attributes(network1, "network_correlated_continuous", **{'num_features': 2, 'covariances': [[1, 0.4],[0.2, 1]]})
        # non-implemented distribution
        with self.assertRaises(NotImplementedError):
            agents_init.initialize_attributes(network1, "network_correlated_continuous", **{"distribution": "notimplemented", "num_features": 3})        
