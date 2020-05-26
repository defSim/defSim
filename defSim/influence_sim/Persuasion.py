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

    @staticmethod
    def spread_influence(network: nx.Graph,
                         agent_i: int,
                         agents_j: List[int] or int,
                         regime: str,
                         dissimilarity_measure: DissimilarityCalculator,
                         attributes: List[str] = None,
                         **kwargs) -> bool:
        """
        Motivation: Models with persuasive social influence can be grounded on the assumption that people are unable to
        communicate their precise opinion position, but rather communicate an argument close to their opinion position.
        We take the opinion position op the sending agent in the model (between 0 and 1) as the probability that this
        agent will communicate argument 1. It is a special case of the opinion 'urn'-model
        where a random argument is drawn from a collection of arguments :math:`O` in the memory of agent :math:`i`,
        containing either pro or con arguments as :math:`\{0,1\}`. Such an 'urn'-based opinion can be transformed to a
        continuous opinion by taking :math:`\dfrac{\sum_{x \in O_i} x}{|O|}`.

        :param network: The network in which the agents exist.
        :param agent_i: The index of the focal agent that is either the source or the target of the influence
        :param agents_j: A list of indices of the agents who can be either the source or the targets of the influence.
            The list can have a single entry, implementing one-to-one communication.
        :param attributes: A list of the names of all the attributes that are subject to influence. If an agent has
            e.g. the attributes "Sex" and "Music taste", only supply ["Music taste"] as a parameter for this function.
            The influence function itself can still be a function of the "Sex" attribute.
        :param regime: Either "one-to-one", "one-to-many" or "many-to-one"
        :param dissimilarity_measure: An instance of
            a :class:`~defSim.dissimilarity_component.DissimilarityCalculator.DissimilarityCalculator`.
        :param kwargs: Additional parameters specific to the implementation of the InfluenceOperator. Possible
            parameters are the following:
        :param float=0.5 convergence_rate: A number between 0 and 1 determining what proportion of the sending agent's
            position the receiving agent will adopt. E.g. when set to 1, the receiving agent assimilates - adopting the
            sending agent's position fully, but when set to 0.5, the receiving agent moves only half-way towards the
            sending agent's position. Passed as a kwargs argument.
        :param float=1 confidence_level: A number between 0 and 1 determining the cutoff value for the dissimilarity
            at which agents do not interact anymore. 1 means that even the most dissimilar agents still interact, 0
            means no interaction. Passed as a kwargs argument.
        :param bool=False bi_directional: A boolean specifying whether influence is bi- or uni-directional.
        :param dict=None feature_bounds: A dictionary with keys 'min' and 'max' to define boundaries of feature range. 
            Defaults to values specified in :class:`~defSim.agents_init.RandomContinuousInitializer.RandomContinuousInitializers`        
        :returns: true if agent(s) were successfully influenced
        """

        # Arguments communicated will be based on extremes of the opinion scale
        # If not specified, default random continuous bounds are assumed
        feature_bounds = kwargs.get("feature_bounds", None)
        if feature_bounds is None:
            feature_bounds = RandomContinuousInitializer.default_feature_bounds

        confidence_level = kwargs.get('confidence_level', 1)
        convergence_rate = kwargs.get('convergence_rate', 0.5)
        bi_directional = kwargs.get('bi_directional', False)

        # in case of one-to-one, j is only one agent, but we still want to iterate over it
        if type(agents_j) != list:
            agents_j = [agents_j]

        if attributes is None:
            # if no specific attributes were given, take all of them
            attributes = list(network.nodes[agent_i].keys())

        # whether influence was exerted
        success = False

        influenced_feature = random.choice(attributes)

        if regime != "many-to-one":
            for neighbor in agents_j:
                if network.edges[agent_i, neighbor]['dist'] < confidence_level:
                    success = True
                    # transform the opinion of agent_i to an argument of the closest opinion pole by randomly drawing
                    # an argument with a probability conditional on the extremity of the opinion
                    argument = random.choices([feature_bounds['min'], feature_bounds['max']], weights=[1-network.nodes[agent_i][influenced_feature],
                                                              network.nodes[agent_i][influenced_feature]])[0]
                    # store the original opinion of the neighbor for bi-directional case
                    argument_neighbor = network.nodes[neighbor][influenced_feature]

                    # calculate 'opinion' distance on the trait that will be changed
                    feature_difference = argument - network.nodes[neighbor][influenced_feature]
                    # influence function
                    network.nodes[neighbor][influenced_feature] = network.nodes[neighbor][influenced_feature] + \
                                                                  convergence_rate * feature_difference
                    if bi_directional == True and regime == "one-to-one":
                        argument = random.choices([feature_bounds['min'], feature_bounds['max']], weights=[1 - argument_neighbor,
                                                                   argument_neighbor])[0]
                        feature_difference = argument - network.nodes[agent_i][influenced_feature]
                        # influence function
                        network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][influenced_feature] + \
                                                                     convergence_rate * feature_difference
                        update_dissimilarity(network, [agent_i, neighbor], dissimilarity_measure, **kwargs)
                    else:
                        update_dissimilarity(network, [neighbor], dissimilarity_measure, **kwargs)

        else:
            # many to one
            close_neighbors = [neighbor for neighbor in agents_j if
                               network.edges[agent_i, neighbor]['dist'] < confidence_level]
            if len(close_neighbors) != 0:
                success = True
                average_value = np.mean([network.nodes[neighbor][influenced_feature] for neighbor in close_neighbors])
                argument = random.choices([feature_bounds['min'], feature_bounds['max']], weights=[1 - average_value, average_value])[0]
                feature_difference = argument - network.nodes[agent_i][influenced_feature]
                network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][influenced_feature] + \
                                                             convergence_rate * feature_difference
                update_dissimilarity(network, [agent_i], dissimilarity_measure, **kwargs)

        return success
    #todo: TESTING