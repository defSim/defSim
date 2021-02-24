from defSim.tools import NetworkDistanceUpdater
from abc import ABC, abstractmethod
import networkx as nx
import networkx.algorithms.isomorphism as iso
from typing import List

class ConvergenceCheck(ABC):
    """
    This class is responsible for testing convergence.
    Inherit from this class and implement the check_convergence method for each type of convergence check.
    """

    @abstractmethod
    def check_convergence(self, network: nx.Graph, **kwargs) -> bool:
        """
        This method receives a NetworkX object and returns whether the simulation has converged or not.

        :param network: A NetworkX graph object.

        :returns: True if converged according to specified criteria, else False. 
        """
        pass


class PragmaticConvergenceCheck(ConvergenceCheck):
    """
    Pragmatic convergence checks whether the structure of the network and all attributes are the same
    as in the previous check. If that's the case, it is assumed that the simulation converged and it stops.

    :param int=100 step_size: determines how often pragmatic convergence should be checked
    """

    def __init__(self, initial_network):
        self._previous_network = initial_network
        all_attributes = initial_network.nodes[1].keys()
        self._node_matcher = iso.categorical_node_match(all_attributes, [0 for i in range(len(all_attributes))])                

    def check_convergence(self, network: nx.Graph, **kwargs) -> bool:
        """
        This method receives a NetworkX object checks whether all attributes and the network structure
        are identical to the stored network from the previous call.

        :param network: A NetworkX graph object.

        :returns: True if no attributes changed and network structure has not changed, else False. 
        """            

        if nx.is_isomorphic(network, self._previous_network, node_match=self._node_matcher):
            return True
        else:
            self._previous_network = network.copy()
            return False


class OpinionDistanceConvergenceCheck(ConvergenceCheck):
    """
    Here the convergence of the simulation is periodically checked by assessing the distance between each neighbor
    in the network. Unless there is no single pair left that can theoretically influence each other, the simulation
    continues.

    :param float maximum: A value that determines above what maximum distance two agents can't influence each other anymore.
    :param float=0.0 minimum: A value that determines below what minimum distance two agents can't influence each other anymore.
    """

    def __init__(self, maximum: float, minimum: float = 0):
        self.maximum = maximum
        self.minimum = minimum

    def check_convergence(self, network: nx.Graph, **kwargs) -> bool:
        """
        This method receives a NetworkX object and checks whether any pair of agents is within the specified
        opinion distance from each other, indicating that they could theoretically be influenced.

        :param network: A NetworkX graph object.

        :returns: True if converged according to specified criteria, else False. 
        """

        # check_dissimilarity returns True if any agents can be influenced
        # invert to return True if no agents can be influenced
        return not NetworkDistanceUpdater.check_dissimilarity(network, maximum=self.maximum, minimum=self.minimum)
                     