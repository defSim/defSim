import networkx as nx
import random
import warnings

from .network_evolution_sim import NetworkModifier


class MaslovSneppenModifier(NetworkModifier):

    def __init__(self, rewiring_prop: float = None, rewiring_exact: int = None):
        super().__init__()
        self.rewiring_prop = rewiring_prop
        self.rewiring_exact = rewiring_exact

    def rewire_network(self, network: nx.Graph, rewiring_prop: float = None, rewiring_exact = None, **kwargs):
        """
        This method executes Maslov Sneppen rewiring [MaslovSneppen2002]_. Until a given proportion of the network
        edges is rewired, the algorithm will pick two edges at random, remove them, and construct an edge between a
        different combination of nodes that have just lost an edge. Effectively, this introduces randomization of network
        structure, while leaving the degree distribution unchanged. Because the parameter `rewiring_prop` functions as a
        threshold for number of rewiring iterations that need to be executed, it can exceed 1. Actually, to achieve a
        random network starting from a network with structure, the rewiring proportion should exceed 1.

        :param network: NetworkX Graph object
        :param rewiring_prop: A threshold for the minimum proportion of edges in the graph object that need to be rewired.
            Sampling these edges happens with replacement, so rewiring_prop may exceed 1.
        :param rewiring_exact: The exact number of edges to rewire. One of rewiring_prop or rewiring_exact must be set.
            If both are set, rewiring_exact takes precedence.
        :return: Does not return the network. The network is modified in place.
        """

        if rewiring_prop is None:
            rewiring_prop = self.rewiring_prop
        if rewiring_exact is None:
            rewiring_exact = self.rewiring_exact

        if rewiring_exact is not None and rewiring_prop is None:
            rewire_n = rewiring_exact
        elif rewiring_exact is None and rewiring_prop is not None:
            rewire_n = rewiring_prop * network.number_of_edges()
        elif rewiring_exact is not None and rewiring_prop is not None:
            rewire_n = rewiring_exact
            warnings.warn("Both proportional and exact rewiring specified, using exact.")
                
        ticker = 0
        while rewire_n > ticker:
            agentA, agentB = random.choice(list(network.edges()))
            agentC, agentD = random.choice(list(network.edges()))
            if((agentA != agentC) and (agentA != agentD) and (agentB != agentC) and (agentB != agentD) and not
               network.has_edge(agentA,agentC) and not network.has_edge(agentB,agentD)):
                network.remove_edge(agentA,agentB)
                network.remove_edge(agentC,agentD)
                network.add_edge(agentA,agentC)
                network.add_edge(agentB,agentD)
                ticker += 1