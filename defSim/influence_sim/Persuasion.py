import random
import warnings

import networkx as nx
from .influence_sim import InfluenceOperator
from ..tools.NetworkDistanceUpdater import update_dissimilarity
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator
from defSim.agents_init.RandomContinuousInitializer import RandomContinuousInitializer
from typing import List
import numpy as np


class Persuasion(InfluenceOperator):
    """
    Models with persuasive social influence can be grounded on the assumption that people are unable to
    communicate their precise opinion position, but rather communicate an argument close to their opinion position.
    We take the opinion position op the sending agent in the model (between 0 and 1) as the probability that this
    agent will communicate argument 1. It is a special case of the opinion 'urn'-model
    where a random argument is drawn from a collection of arguments :math:`O` in the memory of agent :math:`i`,
    containing either pro or con arguments as :math:`\{0,1\}`. Such an 'urn'-based opinion can be transformed to a
    continuous opinion by taking :math:`\dfrac{\sum_{x \in O_i} x}{|O|}`.
    Here, we make use of that relationship and implement an implicit argument communication model.
    agent_i communicates a pro (1) argument on a given topic with a probability equal to their current opinion on
    that topic.

    """
    def __init__(self, regime: str, **kwargs):
        """
        :param regime: This string determines the mode in which the agents influence each other.
              In 'one-to-one' the focal agent influences one other agent, in 'one-to-many' multiple other
              agents and in 'many-to-one' the focal agent is influenced by multiple other agents in the network.      
        :param kwargs: Additional parameters specific to the implementation of the InfluenceOperator. Possible
            parameters are the following:
        :param float=0.2 convergence_rate: A number between 0 and 1 determining the share of the opinion scale the
            receiving agent will move in either direction after interaction.
        :param bool=False bi_directional: A boolean specifying whether influence is bi- or uni-directional.
        :param float=1 confidence_level: A number between 0 and 1 determining the cutoff value for the dissimilarity at
            which agents do not interact anymore. 1 means that only strictly dissimilar agents do not interact, 0 means
            no agents will interact. Passed as a kwargs argument.
       """

        self.regime = regime 

        try:
            self.convergence_rate = kwargs["convergence_rate"]
        except KeyError:
            warnings.warn("convergence_rate not specified, using default value 0.5")
            self.convergence_rate = 0.5

        self.confidence_level = kwargs.get('confidence_level', 1)
        self.bi_directional = kwargs.get('bi_directional', False)

    def spread_influence(self, 
                         network: nx.Graph,
                         agent_i: int,
                         agents_j: List[int] or int,
                         dissimilarity_measure: DissimilarityCalculator,
                         attributes: List[str] = None,
                         **kwargs) -> bool:
        """
        :param network: The network in which the agents exist.
        :param agent_i: The index of the focal agent that is either the source or the target of the influence
        :param agents_j: A list of indices of the agents who can be either the source or the targets of the influence.
            The list can have a single entry, implementing one-to-one communication.
        :param attributes: A list of the names of all the attributes that are subject to influence. If an agent has
            e.g. the attributes "Sex" and "Music taste", only supply ["Music taste"] as a parameter for this function.
            The influence function itself can still be a function of the "Sex" attribute.
        :param dissimilarity_measure: An instance of
            a :class:`~defSim.dissimilarity_component.DissimilarityCalculator.DissimilarityCalculator`.     
        :returns: true if agent(s) were successfully influenced
        """

        # in case of one-to-one, j is only one agent, but we still want to iterate over it
        if type(agents_j) != list:
            agents_j = [agents_j]

        if attributes is None:
            # if no specific attributes were given, take all of them
            attributes = list(network.nodes[agent_i].keys())

        # whether influence was exerted
        success = False

        influenced_feature = random.choice(attributes)

        if self.regime != "many-to-one":
            for neighbor in agents_j:
                if network.edges[agent_i, neighbor]['dist'] < self.confidence_level:
                    success = True
                    # transform the opinion of agent_i to an argument of the closest opinion pole by randomly drawing
                    # an argument with a probability conditional on the extremity of the opinion
                    # and a value equal to the opinion change induced as specified in the convergence_rate
                    argument = random.choices([-self.convergence_rate, self.convergence_rate],
                                              weights=[1-network.nodes[agent_i][influenced_feature],
                                                       network.nodes[agent_i][influenced_feature]])[0]
                    # store the original opinion of the neighbor for bi-directional case
                    opinion_neighbor = network.nodes[neighbor][influenced_feature]

                    # influence function
                    network.nodes[neighbor][influenced_feature] = network.nodes[neighbor][influenced_feature] + argument
                    # bounding the opinions to the pre-supposed opinion scale [0,1]
                    if network.nodes[neighbor][influenced_feature] > 1: network.nodes[neighbor][influenced_feature] = 1
                    if network.nodes[neighbor][influenced_feature] < 0: network.nodes[neighbor][influenced_feature] = 0

                    if self.bi_directional == True and self.regime == "one-to-one":
                        argument = random.choices([-self.convergence_rate, self.convergence_rate],
                                                  weights=[1 - opinion_neighbor, opinion_neighbor])[0]
                        # influence function
                        network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][influenced_feature] + argument
                        update_dissimilarity(network, [agent_i, neighbor], dissimilarity_measure, **kwargs)
                    else:
                        update_dissimilarity(network, [neighbor], dissimilarity_measure, **kwargs)

        else:
            # many to one
            close_neighbors = [neighbor for neighbor in agents_j if
                               network.edges[agent_i, neighbor]['dist'] < self.confidence_level]
            if len(close_neighbors) != 0:
                success = True
                average_value = np.mean([network.nodes[neighbor][influenced_feature] for neighbor in close_neighbors])
                argument = random.choices([-self.convergence_rate, self.convergence_rate],
                                          weights=[1 - average_value, average_value])[0]
                network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][influenced_feature] + argument
                update_dissimilarity(network, [agent_i], dissimilarity_measure, **kwargs)

        return success