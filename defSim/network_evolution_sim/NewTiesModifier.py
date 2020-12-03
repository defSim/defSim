import networkx as nx
import numpy as np
import random
import warnings

from .network_evolution_sim import NetworkModifier


class NewTiesModifier(NetworkModifier):

    def __init__(self, new_ties_probability: float = None):
        super().__init__()
        self.new_ties_probability = new_ties_probability

    def rewire_network(self, network: nx.Graph, new_ties_probability: float = None, **kwargs):
        """
        This function finds all previously unconnected agents in the network and connects them with a given probability.

        :param network: NetworkX Graph object
        :param new_ties_probability: Probability to create new tie between each pair of previously unconnected agents.

        The network is modified in place.
        :returns: Number of edges added.
        """

        if new_ties_probability is None:
            new_ties_probability = self.new_ties_probability
        
        if new_ties_probability is None:
            raise ValueError("No probability given for new tie creation. Pass argument new_ties_probability.")

        try:
            rng = kwargs["np_random_generator"]
        except KeyError:
            warnings.warn("No Numpy Generator in parameter dictionary, creating default")
            rng = np.random.default_rng()
        
        edges_added = 0
        nodes = list(network.nodes)
        for node1 in nodes:
            for node2 in [node for node in nodes if not node == node1 and node not in network.neighbors(node1)]:
                if rng.random() < self.new_ties_probability:
                    network.add_edge(node1, node2)
                    edges_added += 1
                    
        return edges_added