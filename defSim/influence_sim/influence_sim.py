from abc import ABC, abstractmethod
import networkx as nx
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator
from typing import List


class InfluenceOperator(ABC):
    """
    The InfluenceOperator is responsible for executing the influence function of the simulation. The influence function
    can be something like bounded confidence, negative influence or only positive influence.
    """

    @staticmethod
    @abstractmethod
    def spread_influence(network: nx.Graph,
                         agent_i: int,
                         agents_j: List[int] or int,
                         regime: str,
                         dissimilarity_measure: DissimilarityCalculator,
                         attributes: List[str] = None,
                         **kwargs) -> bool:
        """
        This function is responsible for executing the influence process. The call of this function can be seen as an
        interaction between agents that either results in successful influence or not. Unsuccessful influence attempts
        can also be interpreted as no interaction at all. The function returns true if influence was successful.


        :param network: The network in which the agents exist.
        :param agent_i: the index of the focal agent that is either the source or the target of the influence
        :param agents_j: A list of indices of the agents who can be either the source or the targets of the
                influence. The list can have a single entry, implementing one-to-one communication.
        :param attributes: A list of the names of all the attributes that are subject to influence.
                If an agent has e.g. the attributes "Sex" and "Music taste", only supply ["Music taste"] as a
                parameter for this function. The influence function itself can still be a function of the "Sex"
                attribute.
        :param regime: This string determines the mode in which the agents influence each other.
                In 'one-to-one' the focal agent influences one other agent, in 'one-to-many' multiple other
                agents and in 'many-to-one' the focal agent is influenced by multiple other agents in the network.
        :param dissimilarity_measure: An instance of a :class:`~defSim.dissimilarity_component.DissimilarityCalculator.DissimilarityCalculator`.
        :returns: true if agent(s) were successfully influenced
        """
        pass


def spread_influence(network: nx.Graph,
                     realization: str,
                     agent_i: int,
                     agents_j: List[int] or int,
                     regime: str,
                     dissimilarity_measure: DissimilarityCalculator,
                     attributes: List[str] = None,
                     **kwargs) -> bool:
    """
    This function works as a factory method for the influence component.
    It calls either the many_to_one or the one_to_many function of a specific implementation of the InfluenceOperator
    and passes to itt to the kwargs dictionary. Which function is called is based on the selected communication regime.

    :param network: The network that will be modified.
    :param realization: The specific implementation of the InfluenceOperator. Options are "bounded_confidence",
        "axelrod", "weighted_linear", "persuasion".
    :param agent_i: the index of the focal agent that is either the source or the target of the influence
    :param agents_j: A list of indices of the agents who can be either the source or the targets of the influence. The list can have a
    :param attributes: A list of the names of all the attributes that are subject to influence. If an agent has
        e.g. the attributes "Sex" and "Music taste", only supply ["Music taste"] as a parameter for this function.
        The influence function itself can still be a function of the "Sex" attribute.
    :param regime: Either "many_to_one", "one_to_many" or "one_to_one".
    :param dissimilarity_measure: An instance of a :class:`~defSim.dissimilarity_component.DissimilarityCalculator.DissimilarityCalculator`.
    :returns: true if agent(s) were successfully influenced
    """
    from .Axelrod import Axelrod
    from .BoundedConfidence import BoundedConfidence
    from .WeightedLinear import WeightedLinear
    from .Persuasion import Persuasion

    # if both functions get the same arguments?
    if realization == "axelrod":
        return Axelrod.spread_influence(network,
                                        agent_i,
                                        agents_j,
                                        regime,
                                        dissimilarity_measure,
                                        attributes,
                                        **kwargs)
    elif realization == "bounded_confidence":
        return BoundedConfidence.spread_influence(network,
                                                  agent_i,
                                                  agents_j,
                                                  regime,
                                                  dissimilarity_measure,
                                                  attributes,
                                                  **kwargs)
    elif realization == "weighted_linear":
        return WeightedLinear.spread_influence(network,
                                               agent_i,
                                               agents_j,
                                               regime,
                                               dissimilarity_measure,
                                               attributes,
                                               **kwargs)
    elif realization == "persuasion":
        return Persuasion.spread_influence(network,
                                               agent_i,
                                               agents_j,
                                               regime,
                                               dissimilarity_measure,
                                               attributes,
                                               **kwargs)
    else:
        raise ValueError("Can only select from the options ['axelrod', 'bounded_confidence', 'weighted_linear', "
                         "'persuasion]")
