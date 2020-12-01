from typing import List

import networkx as nx
import random
from .focal_agent_sim import FocalAgentSelector


class RandomSelector(FocalAgentSelector):
    """
    Implements the FocalAgentSelector as a uniformly random process
    """

    def __init__(self, **kwargs):
        pass
    
    def select_agent(self, network: nx.Graph, agents: List[int]=[]) -> int:
        """
        This method selects a random agent from a network for the influence process.

        :param network: A NetworkX object from which the agent shall be selected.
        :param agents: A list of the indices of all agents in the network.

        :returns The index of the selected agent.
        """
        if len(agents)==0:
            # this takes a long time for large networks so try to avoid it by passing the list of agents as a parameter
            agents = list(network.nodes)
        return random.choice(agents)
