from .dissimilarity_calculator import DissimilarityCalculator
import numpy as np
import networkx as nx


class EuclideanDistance(DissimilarityCalculator):
    """
    Implements the DissimilarityCalculator as a calculator of the euclidean distance
    """

    @staticmethod
    def calculate_dissimilarity(network: nx.Graph, agent1_id: int, agent2_id: int,
                                **kwargs) -> float:
        """
        Calculates normalized euclidean distance of the agents' feature vectors where feature values do not exceed the
        [0,1] bounds.

        :param network: The network in which the agents exist.
        :param agent1_id: The index of the first agent.
        :param agent2_id: The index of the agent to compare with.

        :returns: A float value, representing the distance between the two agents.
        """

        dissimilarity_exclude = kwargs.get('dissimilarity_exclude', [])

        test = [v for k, v in network.nodes[agent1_id].items() if k not in dissimilarity_exclude]

        agent1_attributes = [v for k, v in network.nodes[agent1_id].items() if k not in dissimilarity_exclude]
        agent2_attributes = [v for k, v in network.nodes[agent2_id].items() if k not in dissimilarity_exclude]

        return np.linalg.norm((np.array(agent1_attributes) - np.array(agent2_attributes)) / np.sqrt(len(agent1_attributes)))

    @staticmethod
    def calculate_dissimilarity_networkwide(network: nx.Graph, **kwargs):
        """
        Calculates the distance from each agent to each other and sets that distance as an attribute on the edge
        between them.

        :param network: The network that is modified.
        """
        #dissimilarity_exclude = kwargs.get('dissimilarity_exclude', [])

        for agent in network.nodes():
            for neighbor in network.neighbors(agent):
                network.edges[agent, neighbor]['dist'] = EuclideanDistance.calculate_dissimilarity(network,
                                                                                                   agent,
                                                                                                   neighbor,
                                                                                                   **kwargs)
