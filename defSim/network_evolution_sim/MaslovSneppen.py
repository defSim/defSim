import networkx as nx

from .network_evolution_sim import NetworkModifier


class MaslovSneppen(NetworkModifier):

    @staticmethod
    def rewire_network(network: nx.Graph, **kwargs):
        """
        This function picks random agents from the network and connects them to each other.

        :param network: The network that is modified.
        """
        pass
