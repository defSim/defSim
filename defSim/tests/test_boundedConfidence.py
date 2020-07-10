from unittest import TestCase
from defSim.influence_sim import BoundedConfidence
from defSim.network_init import network_init
from defSim.agents_init import agents_init
from defSim.dissimilarity_component.EuclideanDistance import EuclideanDistance


class TestBoundedConfidence(TestCase):

    def test_spread_influence(self):
        network1 = network_init.generate_network("grid")
        agents_init.initialize_attributes(network1, "random_continuous", **{"num_features": 1})
        EuclideanDistance().calculate_dissimilarity_networkwide(network1)
        network2 = network_init.generate_network("grid")
        agents_init.initialize_attributes(network2, "random_continuous", **{"num_features": 2})
        EuclideanDistance().calculate_dissimilarity_networkwide(network2)

        BoundedConfidence.BoundedConfidence.spread_influence(network1,
                                                             0,
                                                             [neighbor for neighbor in network1[0]],
                                                             attributes=None,
                                                             regime="one-to-many",
                                                             dissimilarity_measure=EuclideanDistance(),
                                                             **{"confidence_level": 0.9})
        BoundedConfidence.BoundedConfidence.spread_influence(network1,
                                                             0,
                                                             [neighbor for neighbor in network1[0]],
                                                             attributes=None,
                                                             regime="many-to-one",
                                                             dissimilarity_measure=EuclideanDistance(),
                                                             **{"confidence_level": 0.9})
        BoundedConfidence.BoundedConfidence.spread_influence(network2,
                                                             0,
                                                             [neighbor for neighbor in network2[0]],
                                                             attributes=None,
                                                             regime="one-to-many",
                                                             dissimilarity_measure=EuclideanDistance(),
                                                             **{"confidence_level": 0.9})
        BoundedConfidence.BoundedConfidence.spread_influence(network2,
                                                             0,
                                                             [neighbor for neighbor in network2[0]],
                                                             attributes=None,
                                                             regime="many-to-one",
                                                             dissimilarity_measure=EuclideanDistance(),
                                                             **{"confidence_level": 0.9})


