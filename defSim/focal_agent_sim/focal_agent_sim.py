from abc import ABC, abstractmethod
import networkx as nx
from typing import List
import inspect


class FocalAgentSelector(ABC):
    """
    This class is responsible for sampling the focal agent for the influence process.
    """
    
    def __init__(self, **kwargs):
        """
        :param kwargs: This dictionary contains all the implementation-specific parameters.
        """
        pass

    @abstractmethod
    def select_agent(network: nx.Graph, agents: List[int]=[]) -> int:
        """
        This method selects an agent from a network for the influence process.
        Based on the communication regime, the selected agent is either the source or the target of influence.

        :param network: A NetworkX object from which the agent shall be selected.
        :param agents: A list of the indices of all agents in the network

        :returns The index of the selected agent.
        """
        pass

def select_focal_agent(network: nx.Graph, realization: str or FocalAgentSelector, agents: List[int]=[], **kwargs) -> int:
    """
    This function works as a factory method for the FocalAgentSelector component.
    It calls the select_agent function of a specific implementation of the FocalAgentSelector and passes to it
    the kwargs dictionary.

    :param network: A NetworkX object from which the focal agent will be selected
    :param realization: The specific FocalAgentSelector that shall be used to sample the focal agent. Options are "random", ...
    :param agents: A list of the indices of all agents in the network.

    :returns The index of the focal agent in the network.
    """
    from .RandomSelector import RandomSelector

    if realization == "random":
        return RandomSelector(**kwargs).select_agent(network, agents)
    elif isinstance(realization, FocalAgentSelector):
        return realization.select_agent(network, agents)
    else:
        raise ValueError("Can only select from the options ['random'] or input an instance of a class which inherits from FocalAgentSelector")
