from abc import ABC, abstractmethod
from typing import Iterable


import networkx as nx


class NeighborSelector(ABC):
    """
    The NeighborSelector is responsible for picking certain agents from the environment of the focal agent.
    These agents are then either the source or the target in the following influence step.
    Possible ways to select neighbors is either by picking all other agents, i.e. global influence (simulation influence
    from news and polls), all neighbors in the immediate neighborhood, or only single neighbors.
    """

    def __init__(self, **kwargs):
        pass    

    @abstractmethod
    def select_neighbors(self, network: nx.Graph, focal_agent: int, regime: str, **kwargs) -> Iterable[int]:
        """
        This method selects a subset of agents from the network that are in some way relevant for the
        influence process regarding the focal agent.
        This subset could be e.g. a single agent from the direct neighborhood, the whole neighborhood, or all
        agents, excluding the focal agent.



        :param network: the network from which the agent shall be selected.
        :param focal_agent: the index of the focal agent, who is either the source or target of influence.
        :param regime: Whether the focal agent interacts with only one or many agents from his or her
            neighborhood. If "one-to-one": One neighbor to which the focal agent has an outgoing tie is selected.
            If "one-to-many": All neighbors to which the focal agent has an outgoing tie are selected.
            If "many-to-one": All neighbors from which the focal agent has an incoming tie are selected.
        :param kwargs: Additional parameters specific to the implementation of the neighborSelector.

        :returns: a list of the indices of the relevant other agents.
        """
        pass

def select_neighbors(network: nx.Graph, realization: str, focal_agent: int, regime: str, **kwargs) -> Iterable[int]:
    """
    This function works as a factory method for the neighborSelector component.
    It calls the select_neighbors function of the specific neighborSelector and passes to it the index of the
    focal agent and the communication regime.

    :param network: The network from which the agents are selected.
    :param realization: The specific implementation of the neighborSelector. Options are "random", "similar"
    :param focal_agent: An integer that represents the index of the focal agent in the network.
    :param regime: Either "many_to_one", "one_to_many" or "one_to_one".
    :param kwargs: Additional parameters specific to the implementation of the neighborSelector.
    :returns: A list with the indices of the selected other agents.
    """
    from .RandomNeighborSelector import RandomNeighborSelector
    from .SimilarNeighborSelector import SimilarNeighborSelector

    if realization == "random":
        return RandomNeighborSelector().select_neighbors(network, focal_agent, regime, **kwargs)
    elif realization == "similar":
        return SimilarNeighborSelector().select_neighbors(network, focal_agent, regime, **kwargs)
    elif isinstance(realization, NeighborSelector):
        return realization.select_neighbors(network, focal_agent, regime, **kwargs)
    else:
        raise ValueError("Can only select from the options ['random', 'similar']")

