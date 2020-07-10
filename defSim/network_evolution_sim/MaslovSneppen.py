import networkx as nx

from .network_evolution_sim import NetworkModifier


class MaslovSneppen(NetworkModifier):

    @staticmethod
    def rewire_network(network: nx.Graph, rewiring_prop: float, **kwargs):
        """
        This method executes Maslov Sneppen rewiring (Maslov & Sneppen, 2002). Until a given proportion of the network
        edges is rewired, the algorithm will pick two edges at random, remove them, and construct an edge between a
        different combination of nodes that have just lost an edge. Effectively, this introduces randomization of network
        structure, while leaving the degree distribution unchanged. Because the parameter `rewiring_prop` functions as a
        threshold for number of rewiring iterations that need to be executed, it can exceed 1. Actually, to achieve a
        random network starting from a network with structure, the rewiring proportion should exceed 1.

        :param network: NetworkX Graph object
        :param rewiring_prop: A threshold for the minimum proportion of edges in the graph object that need to be rewired.
            Sampling these edges happens with replacement, so rewiring_prop may exceed 1.
        :return: Does not return the network. The network is modified in place.
        """
        ticker = 0
        while rewiring_prop * network.number_of_edges() > ticker:
            agentA, agentB = random.choice(list(network.edges()))
            agentC, agentD = random.choice(list(network.edges()))
            if((agentA != agentC) & (agentA != agentD) & (agentB != agentC) & (agentB != agentD) &
               (network.has_edge(agentA,agentC)==False) & (network.has_edge(agentB,agentD)==False)):
                network.remove_edge(agentA,agentB)
                network.remove_edge(agentC,agentD)
                network.add_edge(agentA,agentC)
                network.add_edge(agentB,agentD)
                ticker += 1
        

