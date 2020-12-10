from unittest import TestCase
from defSim.dissimilarity_component.HammingDistance import HammingDistance
from defSim.dissimilarity_component.EuclideanDistance import EuclideanDistance
from defSim.network_init import network_init
from defSim.agents_init import agents_init
import math


class TestDissimilarityCalculator(TestCase):
    networkTest = network_init.generate_network("grid")
    networkCategorical = network_init.generate_network("grid")
    networkContinuous = network_init.generate_network("grid")


    def test_HammingDistance_calculate_dissimilarity(self):
        self.networkTest.nodes[0]["a"] = 0.5
        self.networkTest.nodes[0]["b"] = 0.6
        self.networkTest.nodes[1]["a"] = 0.3
        self.networkTest.nodes[1]["b"] = 0.6
        self.assertEqual(HammingDistance().calculate_dissimilarity(self.networkTest,0,1), 0.5)
    def test_HammingDistance_calculate_dissimilarity_networkwide(self):
        agents_init.initialize_attributes(self.networkCategorical, "random_categorical")
        agents_init.initialize_attributes(self.networkContinuous, "random_continuous")
        HammingDistance().calculate_dissimilarity_networkwide(self.networkContinuous)
        HammingDistance().calculate_dissimilarity_networkwide(self.networkCategorical)

    networkCategorical2 = network_init.generate_network("grid")
    networkContinuous2 = network_init.generate_network("grid")
    def test_EuclideanDistance_calculate_dissimilarity(self):
        self.networkTest.nodes[0]["a"] = 0.5
        self.networkTest.nodes[1]["a"] = 0.3
        self.assertEqual(EuclideanDistance().calculate_dissimilarity(self.networkTest,0,1), 0.2)
        self.networkTest.nodes[0]["b"] = 0.2
        self.networkTest.nodes[1]["c"] = 0.8
        self.assertEqual(EuclideanDistance().calculate_dissimilarity(self.networkTest,0,1), math.sqrt((0.5-0.3)**2+(0.2-0.8)**2) / math.sqrt(2))


    def test_EuclideanDistance_calculate_dissimilarity_networkwide(self):
        agents_init.initialize_attributes(self.networkCategorical2, "random_categorical")
        agents_init.initialize_attributes(self.networkContinuous2, "random_continuous")
        EuclideanDistance().calculate_dissimilarity_networkwide(self.networkContinuous2)
        EuclideanDistance().calculate_dissimilarity_networkwide(self.networkCategorical2)
