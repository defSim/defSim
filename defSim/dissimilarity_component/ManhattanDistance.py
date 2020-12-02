from .dissimilarity_calculator import DissimilarityCalculator
import networkx as nx

class ManhattanDistance(DissimilarityCalculator):
    """
    Implements the DissimilarityCalculator as a calculator of the Manhattan distance

    The class contains the attribute 'exclude' which accepts a list of strings with the names of agent features that
    should not be used to calculate between agent similarity.
    """

    def __init__(self, exclude=[]):
        self.exclude = exclude

    def calculate_dissimilarity(self, network: nx.Graph, agent1_id: int, agent2_id: int) -> float:
        """
        Computes the Manhattan Distance between two Agents, i.e. returns the sum of absolute
        differences between agent1 and agent2 on each attribute.

        :param network: The network in which the agents exist.
        :param agent1_id: The index of the first agent.
        :param agent2_id: The index of the agent to compare with.

        :returns a float value, representing the distance between the two agents
        """
        number_of_features = len(network.nodes[agent1_id])

        if not len(network.nodes[agent2_id]) == number_of_features:
            raise KeyError('Dissimilarity calculation failed because agent1 and agent2 do not have te same number of attributes.')
        
        # calculate absolute differences between agent1 and agent2 on each feature except those listed in exclude
        abs_differences = [abs(network.nodes[agent2_id][k] - network.nodes[agent1_id][k]) for k in network.nodes[agent1_id] if k not in self.exclude]
        # take the sum of absolute differences
        sum_abs_differences = sum(abs_differences)
        # return the sum of absolute differences, divided by the number of features
        return sum_abs_differences / number_of_features

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
