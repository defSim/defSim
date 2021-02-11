from abc import ABC, abstractmethod
import networkx as nx


class NetworkModifier(ABC):
    """
    The NetworkModifier changes the structure of the network. It can build or remove edges based on how agents are
    connected and what attributes they have.
    """

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def rewire_network(self, network: nx.Graph, **kwargs):
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
    from .MaslovSneppenModifier import MaslovSneppenModifier
    from .NewTiesModifier import NewTiesModifier
    if realization == "maslov_sneppen":
        rewiring_prop = kwargs.get('rewiring_prop', None)
        rewiring_exact = kwargs.get('rewiring_exact', None)
        MaslovSneppenModifier(rewiring_prop = rewiring_prop, rewiring_exact = rewiring_exact).rewire_network(network, **kwargs)
    elif realization == "new_ties":
        new_ties_probability = kwargs.get('new_ties_probability', None)
        NewTiesModifier(new_ties_probability = new_ties_probability).rewire_network(network, **kwargs)
    elif isinstance(realization, NetworkModifier):
        realization.rewire_network(network)
    else:
        raise ValueError("Can only select from the options ['maslov_sneppen', 'new_ties'] or provide an instance of NetworkModifier")
