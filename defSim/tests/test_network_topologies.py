from unittest import TestCase
from defSim.network_init import network_init
import networkx as nx

def test_spatial_random_graph():
    graph = network_init.generate_network("spatial_random_graph", **{"num_agents": 16, "min_neighbors": 8})

    assert type(graph) is nx.Graph


class TestGenerate_network(TestCase):
    def test_generate_network(self):
        graph = network_init.generate_network("spatial_random_graph")
        self.assertEqual(type(graph), nx.Graph)

        graph = network_init.generate_network("cycle_graph", **{"n": 30})
        self.assertEqual(type(graph), nx.Graph)




