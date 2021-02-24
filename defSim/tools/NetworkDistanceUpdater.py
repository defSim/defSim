from typing import List
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator
import networkx as nx


def update_dissimilarity(network: nx.Graph, agents: List[int], calculator: DissimilarityCalculator, **kwargs):
    """
    This method recomputes the edges between a certain set of agents and all their neighbors and then modifies
    the edges between them respectively.

    :param calculator: An implementation of the DissimilarityCalculator class
    :param network: The network that is updated.
    :param agents: A list containing the indices of all agents whose edges should be updated.
    """
    for agent in agents:  # all ties in Graph and all outgoing ties in DiGraph
        for neighbor in network.neighbors(agent):
            network.edges[agent, neighbor]['dist'] = calculator.calculate_dissimilarity(network,
                                                                                        agent,
                                                                                        neighbor)
        try:  # for incoming ties in DiGraphs
            for neighbor in network.predecessors(agent):
                network.edges[neighbor, agent]['dist'] = calculator.calculate_dissimilarity(network,
                                                                                            agent,
                                                                                            neighbor)
        except:
            pass


def check_dissimilarity(network: nx.Graph, maximum: float, minimum: float = 0):
    """
    This function is used to check whether influence is theoretically still possible. For that is checked whether
    any edge has a dissimilarity value inbetween a certain range of possible values that allow for further influence
    steps. This range has 1 as the upper limit and a given threshold as lower limit.

    :param network: The network that is checked.
    :param maximum: The upper limit of dissimilarity that makes it possible for agents to influence each other.
        Only edges with dissimilarity strictly lower than this value allow influence.
    :param minimum: The lower limit of dissimilarity that makes it possible for agents to influence each other.
        Only edges with dissimilarity strictly greater than this value allow influence.
    :returns: True if there is still change possible, False otherwise

    """

    return any(minimum < val < maximum for key, val in nx.get_edge_attributes(network, 'dist').items())
