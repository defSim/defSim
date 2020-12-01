import random
from typing import Iterable

import networkx as nx

from .neighbor_selector_sim import NeighborSelector


class SimilarNeighborSelector(NeighborSelector):
    """
    Implements the neighborSelector such that neighbors with a similar cultural profile are selected. Either all
    neighbors are selected - in the case of one-to-many and many-to-one communication - or a random neighbor - in the
    case of one-to-one communication.
    """

    def select_neighbors(self, network: nx.Graph, focal_agent: int, regime: str,
                         confidence_level_neighbor_selector: float = .5, **kwargs) -> Iterable[int]:
        """
        Selects a random agent from the direct neighborhood of the focal agent that is within the specified cultural
        distance, as stored in the edge between the focal agent and the potential selected neighbor. If the regime is
        "one-to-many" or "many-to-one", all neighbors within the confidence criterion are selected. When there are no
        eligible neighbors (i.e. the focal agent is too dissimilar from all his neighbors), an empty list is returned.

        :param network: A NetworkX object
        :param focal_agent: The index of the focal agent, who is either the source (for "one-to-one" or "one-to-many"
            communication) or target (for "many-to-one") of influence.
        :param regime: Whether the focal agent interacts with only one or many agents from his or her
            neighborhood.
            If "one-to-one": One neighbor to which the focal agent has an outgoing tie is selected.
            If "one-to-many": All neighbors to which the focal agent has an outgoing tie are selected.
            If "many-to-one": All neighbors from which the focal agent has an incoming tie are selected.
        :param confidence_level_neighbor_selector: The confidence level, i.e. the maximal allowed cultural distance
            between two nodes as stored in their edge attribute "dist"
        :param kwargs: Additional parameters specific to the implementation of the InfluenceOperator.
        :raises: ValueError if not one of the possible options for the communication_regime is chosen.
        :returns: A list of the indices of the relevant other agents.
        """

        eligible_neighbors = [neighbor for neighbor in network[focal_agent]
                              if network.edges[focal_agent,neighbor]['dist'] <= confidence_level_neighbor_selector]

        if eligible_neighbors == []:
            return []
        else:
            if regime == "one-to-one":
                return [random.choice(eligible_neighbors)]
            elif regime == "one-to-many":
                return eligible_neighbors
            elif regime == "many-to-one":
                return eligible_neighbors
            else:
                raise ValueError("You can only select from the options ['one-to-one', 'one-to-many', 'many-to-one']")

