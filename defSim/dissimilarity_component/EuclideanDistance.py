from .dissimilarity_calculator import DissimilarityCalculator
import numpy as np
import networkx as nx


class EuclideanDistance(DissimilarityCalculator):
    """
    Implements the DissimilarityCalculator as a calculator of the euclidean distance
    """

    @staticmethod
    def calculate_dissimilarity(network: nx.Graph, agent1_id: int, agent2_id: int) -> float:
        """
        Calculates euclidean distance of the agents' feature vectors.

        :param network: The network in which the agents exist.
        :param agent1_id: The index of the first agent.
        :param agent2_id: The index of the agent to compare with.

        :returns: A float value, representing the distance between the two agents.
        """
        agent1_attributes = np.array(list(network.nodes[agent1_id].values()))
        agent2_attributes = np.array(list(network.nodes[agent2_id].values()))
        return np.linalg.norm(agent1_attributes - agent2_attributes)

    @staticmethod
    def calculate_dissimilarity_networkwide(network: nx.Graph):
        """
        Calculates the distance from each agent to each other and sets that distance as an attribute on the edge
        between them.

        :param network: The network that is modified.
        """
        for agent in network.nodes():
            for neighbor in network.neighbors(agent):
                network.edges[agent, neighbor]['dist'] = EuclideanDistance.calculate_dissimilarity(network,
                                                                                                    agent,
                                                                                                    neighbor)
