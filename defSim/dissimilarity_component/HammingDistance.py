from .dissimilarity_calculator import DissimilarityCalculator
import networkx as nx


class HammingDistance(DissimilarityCalculator):
    """
    Implements the DissimilarityCalculator as a calculator of the Hamming distance
    """

    @staticmethod
    def calculate_dissimilarity(network: nx.Graph, agent1_id: int, agent2_id: int) -> float:
        """
        Computes the Hamming Distance between two Agents, i.e. returns the proportion of features that
        the two agents have not in common. 1 means therefore total dissimilarity, and 0 is total overlap.
        Only works with categorical attributes.

        :param network: The network in which the agents exist.
        :param agent1_id: The index of the first agent.
        :param agent2_id: The index of the agent to compare with.

        :returns a float value, representing the distance between the two agents
        """
        # todo: implement in such a way that only categorical attributes are considered, and others are ignored
        number_of_features = len(network.node[agent1_id])
        return len([k for k in network.node[agent1_id] if
                    network.node[agent1_id][k] != network.node[agent2_id][k]]) / number_of_features

    @staticmethod
    def calculate_dissimilarity_networkwide(network: nx.Graph):
        """
        Calculates the distance from each agent to each other and sets that distance as an attribute on the edge
        between them.

        :param network: The network that is modified.
        """
        for agent in network.nodes():
            for neighbor in network.neighbors(agent):
                network.edges[agent, neighbor]['dist'] = HammingDistance.calculate_dissimilarity(network, agent,
                                                                                                  neighbor)
