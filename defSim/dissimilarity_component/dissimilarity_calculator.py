from abc import ABC, abstractmethod
import networkx as nx

class DissimilarityCalculator(ABC):
    """
    This class is responsible for determining the distance between nodes, either from one node to another,
    or for every agent in the network to another. The distance could be based on their attributes or actual geodesic
    distance.

    The class contains the attribute 'exclude' which accepts a list of strings with the names of agent features that
    should not be used to calculate between agent similarity.
    """

    def __init__(self, exclude=None):
        # documentation omitted
        self.exclude = exclude

    @abstractmethod
    def calculate_dissimilarity(self, network: nx.Graph, agent1_id: int, agent2_id: int) -> float:
        """
        This function calculates how dissimilar two agents are based on their attributes and/or their distance in
        the network.
        Can for example be used to determine whether a neighbor is selected for the influence process.

        :param network: The network in which the agents exist.
        :param agent1_id: The index of the first agent.
        :param agent2_id: The index of the agent to compare with.

        :returns a float value, representing the distance between the two agents
        """
        pass

    @abstractmethod
    def calculate_dissimilarity_networkwide(self, network: nx.Graph):
        """
        Calculates the distance from each agent to each other and sets that distance as an attribute on the edge
        between them.

        :param network: The network that is modified.
        """
        pass


def select_calculator(realization: str) -> DissimilarityCalculator:
    """
    This function works as a factory method for the dissimilarity_component.
    It returns an instance of the Calculator that is asked for.

    :param realization: The type of DissimilarityCalculator. Possible options are ["hamming", "euclidean", "manhatttan"]
    :return: An instance of a DissimilarityCalculator
    """
    from .HammingDistance import HammingDistance
    from .EuclideanDistance import EuclideanDistance
    from .ManhattanDistance import ManhattanDistance

    if realization == "hamming":
        return HammingDistance()
    elif realization == "euclidean":
        return EuclideanDistance()
    elif realization == "manhattan":
        return ManhattanDistance() 
    else:
        raise ValueError("Can only select from the options ['hamming', 'euclidean']")
