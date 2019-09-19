from abc import ABC, abstractmethod
import networkx as nx


class NetworkModifier(ABC):
    """
    The NetworkModifier changes the structure of the network. It can build or remove edges based on how agents are
    connected and what attributes they have.
    """

    @staticmethod
    @abstractmethod
    def rewire_network(network: nx.Graph, **kwargs):
        """
        Creates new connections or deletes existing ones. Can be used to implement coevolution of networks and model
        selection processes.

        :param network: The network that will be modified.
        """
        pass


def rewire_network(network: nx.Graph, realization: str, **kwargs):
    """

    This function works as a factory method for the NetworkModifier component.
    It calls the rewire_network method of a specific implementation of the AttributesInitializer and passes to it
    the kwargs dictionary.

    :param network: The network that will be modified.
    :param realization: The specific NetworkModifier that shall be used to initialize the attributes. Options are "maslov_sneppen", ..
    :param kwargs: The parameter dictionary with all optional parameters.
    """
    from .NetworkHomophily import MaslovSneppen
    if realization == "maslov_sneppen":
        MaslovSneppen.rewire_network(network, **kwargs)
    elif realization == "alternative1":
        print("implement alternative initialization")
    else:
        raise ValueError("Can only select from the options ['random', 'Alternative1', 'Alternative2']")
