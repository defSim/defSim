import unittest
from unittest import TestCase
from defSim import Simulation
from defSim.dissimilarity_component.EuclideanDistance import EuclideanDistance
from defSim.network_init import network_init
from defSim.agents_init import agents_init
from defSim.network_evolution_sim import network_evolution_sim
from defSim.network_evolution_sim.MaslovSneppenModifier import MaslovSneppenModifier


class TestNetworkRewiring(TestCase):

    network = network_init.generate_network("grid")

    def test_rewire_network(self):
        initial_edges = list(self.network.edges)
        network_evolution_sim.rewire_network(network = self.network, realization = 'maslov_sneppen', **{"rewiring_prop": 0.1})
        self.assertNotEqual(initial_edges, list(self.network.edges))

    @unittest.expectedFailure
    def test_rewire_network_bad_realization(self):
        network_evolution_sim.rewire_network(network = self.network, realization = 'thisisnotreal')

    def test_MaslovSneppen(self):
        initial_edges = list(self.network.edges)
        MaslovSneppenModifier(rewiring_prop = 0.1).rewire_network(network = self.network)
        self.assertNotEqual(initial_edges, list(self.network.edges))

        initial_edges = list(self.network.edges)
        MaslovSneppenModifier(rewiring_exact = 4).rewire_network(network = self.network)
        self.assertNotEqual(initial_edges, list(self.network.edges))

        initial_edges = list(self.network.edges)
        MaslovSneppenModifier(rewiring_prop = 0.1, rewiring_exact = 10).rewire_network(network = self.network)
        self.assertNotEqual(initial_edges, list(self.network.edges))                


class TestNetworkInitializationModifiers(TestCase):

    def test_from_network_init(self):
        network_init.generate_network("grid", network_modifiers = [MaslovSneppenModifier(rewiring_prop = 0.1)])        

    def test_from_simulation_init(self):
        sim = Simulation(
            topology = "grid",
            network_modifiers = [MaslovSneppenModifier(rewiring_prop = 0.1)]
            )

    def test_deprecated_parameter_dict(self):
        with self.assertWarns(DeprecationWarning):
            sim = Simulation(
                topology = "grid",
                parameter_dict = {
                'ms_rewiring': 0.1
                }
                )
            sim.initialize()