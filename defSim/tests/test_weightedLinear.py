from unittest import TestCase
from defSim.influence_sim import WeightedLinear
from defSim.network_init import network_init
from defSim.agents_init import agents_init
from defSim.dissimilarity_component.EuclideanDistance import EuclideanDistance


class TestWeightedLinear(TestCase):

    def test_spread_influence(self):
        network1 = network_init.generate_network("grid", **{"num_agents": 4})
        agents_init.initialize_attributes(network1, "random_continuous", **{"num_features": 1})
        EuclideanDistance.calculate_dissimilarity_networkwide(network1)

        # run one instance to see if it doesn't break (most simple test)
        WeightedLinear.WeightedLinear.spread_influence(network1,
                                                       0,
                                                       [neighbor for neighbor in network1[0]],
                                                       attributes=None,
                                                       regime="one-to-many",
                                                       dissimilarity_measure=EuclideanDistance(),
                                                       **{"convergence_rate": 0.5,
                                                          "homophily": 1,
                                                          "bi_directional": False})

        # with bi-directional influence, let two agents find agreement
        WeightedLinear.WeightedLinear.spread_influence(network1,
                                                       1, #sending agent
                                                       0, #receiving agent
                                                       attributes=None,
                                                       regime="one-to-one",
                                                       dissimilarity_measure=EuclideanDistance(),
                                                       **{"convergence_rate": 0.5,
                                                          "homophily": 0,
                                                          "bi_directional": True})
        self.assertEqual(network1.node[1]['f01'], network1.node[0]['f01'])

