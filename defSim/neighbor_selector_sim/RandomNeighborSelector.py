import random
from typing import Iterable

import networkx as nx

from .neighbor_selector_sim import NeighborSelector


class RandomNeighborSelector(NeighborSelector):
    """
    Implements the neighborSelector in such a way that either all neighbors are selected in the case of
    one-to-many and many-to-one communication, or a random neighbor in the case of one-to-one communication.
    """

    def select_neighbors(self, network: nx.Graph, focal_agent: int, regime: str, **kwargs) -> Iterable[int]:
        """
        Selects a random agent from the direct neighborhood of the focal agent in the case of one-to-one communication,
        and all direct neighbors otherwise.

        :param network: A NetworkX object
        :param focal_agent: The index of the focal agent, who is either the source (for "one-to-one" or "one-to-many"
            communication) or target (for "many-to-one") of influence.
        :param regime: Whether the focal agent interacts with only one or many agents from his or her
            neighborhood. If "one-to-one": One neighbor to which the focal agent has an outgoing tie is selected.
            If "one-to-many": All neighbors to which the focal agent has an outgoing tie are selected.
            If "many-to-one": All neighbors from which the focal agent has an incoming tie are selected.
        :param kwargs: Additional parameters specific to the implementation of the InfluenceOperator.
        :raises: ValueError if not one of the possible options for the communication_regime is chosen.
        :returns: A list of the indices of the relevant other agents.
        """
        if regime == "one-to-one":
            try:  # workaround for graphs where some agents do not have any neighbors (random.choice does not like choosing from empty list)
                return [(random.choice([neighbor for neighbor in network[focal_agent]]))]
            except:
                return []
        elif regime == "one-to-many":
            return [neighbor for neighbor in network[focal_agent]] #todo: implement directed graphs
        elif regime == "many-to-one":
            return [neighbor for neighbor in network[focal_agent]]
        else:
            raise ValueError("You can only select from the options ['one-to-one', 'one-to-many', 'many-to-one']")

