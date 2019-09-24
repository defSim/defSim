from abc import ABC, abstractmethod
import networkx as nx
from typing import List

class OutputTableCreator(ABC):
    """
    This class is responsible for creating the output table.
    """
    @staticmethod
    @abstractmethod
    def create_output(network: nx.Graph, **kwargs) -> int:
        """
        This method receives a NetworkX object, performs some calculation, and outputs a cell for the output table.

        :param network: A NetworkX graph object.

        :returns #todo: a tuple?
        """
        pass

def create_output_table(network: nx.Graph, realizations: List[str]=[], colnames: List[str]=[], agents: List[int]=[], **kwargs) -> int:
    """
    This function works as a factory method for the OutputTableCreator component.
    It calls the create_output function of a specific implementation of the OutputTableCreator and passes to it
    the kwargs dictionary.

    :param network: A NetworkX object from which the focal agent will be selected
    :param realization: The specific OutputTableCreator that will be used. Options are for example ... #todo: add options
    :param agents: A list of the indices of all agents that will be considered by the output table.

    :returns The index of the focal agent in the network.
    """
    if agents != []:
        removenodes = list(set(list(network.nodes())) - set(agents))
        for i in removenodes:
            network.remove_node(i)

    from .OutputMeasures import ClusterFinder

    output = dict()

    if "ClusterFinder" in realizations:
        output['ClusterFinder'] = ClusterFinder.create_output(network, **kwargs)

    if colnames != []:
        for i in colnames:
            output[i] = output.pop(realizations[colnames.index(i)])

    return output