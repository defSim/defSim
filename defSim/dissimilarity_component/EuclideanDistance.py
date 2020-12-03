from .dissimilarity_calculator import DissimilarityCalculator
import numpy as np
import networkx as nx

class EuclideanDistance(DissimilarityCalculator):
    """
    Implements the DissimilarityCalculator as a calculator of the euclidean distance

    The class contains the attribute 'exclude' which accepts a list of strings with the names of agent features that
    should not be used to calculate between agent similarity.
    """

    def __init__(self, exclude=[]):
        # documentation omitted
        self.exclude = exclude

    def calculate_dissimilarity(self, network: nx.Graph, agent1_id: int, agent2_id: int) -> float:
        """
        Calculates normalized euclidean distance of the agents' feature vectors where feature values do not exceed the
        [0,1] bounds.

        The distances are adjusted by the square root of the number of features, so that maximally dissimilar agents
        always have a distance of 1 regardless of the number of features.

        :param network: The network in which the agents exist.
        :param agent1_id: The index of the first agent.
        :param agent2_id: The index of the agent to compare with.

        :returns: A float value, representing the distance between the two agents.
        """

        agent1_attributes = [v for k, v in network.nodes[agent1_id].items() if k not in self.exclude]
        agent2_attributes = [v for k, v in network.nodes[agent2_id].items() if k not in self.exclude]

        return np.linalg.norm(np.array(agent1_attributes) - np.array(agent2_attributes)) / np.sqrt(len(agent1_attributes))

    def calculate_dissimilarity_networkwide(self, network: nx.Graph, **kwargs):
        """
        Calculates the distance from each agent to each other and sets that distance as an attribute on the edge
        between them.

        :param network: The network that is modified.
        """

        for agent in network.nodes():
            for neighbor in network.neighbors(agent):
                network.edges[agent, neighbor]['dist'] = self.calculate_dissimilarity(network,
                                                                                      agent,
                                                                                      neighbor)
