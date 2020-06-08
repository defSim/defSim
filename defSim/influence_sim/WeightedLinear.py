import random

import networkx as nx
from .influence_sim import InfluenceOperator
from ..tools.NetworkDistanceUpdater import update_dissimilarity
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator
from defSim.agents_init.RandomContinuousInitializer import RandomContinuousInitializer
from typing import List
import numpy as np


class WeightedLinear(InfluenceOperator):

    @staticmethod
    def spread_influence(network: nx.Graph,
                         agent_i: int,
                         agents_j: List[int] or int,
                         regime: str,
                         dissimilarity_measure: DissimilarityCalculator,
                         attributes: List[str] = None,
                         **kwargs) -> bool:
        """
        The weighted linear influence function implements the experienced opinion shift as a function of the
        pre-interaction cultural or opinional distance between the agents involved. The ``homophily`` parameter controls
        the steepness of the attraction/repulsion curve. Formally:

        .. math:: o_{i,t+1} = o_{i,t} + \\textrm{convergence_rate} \\cdot (1 - \\textrm{homophily} | o_{j} - o_{it} |)

        Thereafter, opinions are bounded such that they never fall outside the range :math:`[0,1]`

        Crucial is the homophily parameter. The higher its value, the smaller the shift of the receiving
        agent in the direction of the sending agent will be. With this parameter, we can integrate ideas of positive,
        moderated positive, and negative influence into one functional model.

        Three critical values for the ``homophily`` parameter:

        * homophily == 0: only positive influence, the agents exhibit no preference for like-minded others.
        * homophily > 0: moderated positive influence, the agents exhibit a preference for like-minded others and move
          less towards the sender as their distance increases.
        * homophily > 1: moderated postive influence AND negative influence, the agents exhibit a preference for
          like-minded others and move less towards the sender as their distance increases, until distance
          :math:`1 / \\textrm{homophily}` where agents experience a push away from the sending agent.

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
        :param float=0 homophily: A number :math:`\geq` 0 that controls the shape of the influence curve. At 0, agents
            do not show a preference for similar others (only positive influence). At 1, agents more strongly adjust
            their opinion when confronted with similar others (moderated positive influence). At values > 1, there
            exists a point at which influence becomes negative, making agents shift away from the sending agents
            expressed opinion.
        :param bool=False bi_directional: A boolean specifying whether influence is bi- or uni-directional.
        :param dict=None feature_bounds: A dictionary with keys 'min' and 'max' to define boundaries of feature range. 
            Defaults to values specified in :class:`~defSim.agents_init.RandomContinuousInitializer.RandomContinuousInitializers`
        :returns: true if agent(s) were successfully influenced
        """

        try:
            convergence_rate = kwargs["convergence_rate"]
        except KeyError:
            convergence_rate = 0.5
        try:
            homophily = kwargs["homophily"]
        except KeyError:
            homophily = 0

        try:
            bi_directional = kwargs["bi_directional"]
        except KeyError:
            # show error message only in the relevant case
            # if regime == "one-to-one":
            # print("Bi-directionality was not specified, default value False is used.")
            bi_directional = False


        feature_bounds = kwargs.get("feature_bounds", None)
        if feature_bounds is None:
            feature_bounds = RandomContinuousInitializer.default_feature_bounds

        # in case of one-to-one, j is only one agent, but we still want to iterate over it
        if type(agents_j) != list:
            agents_j = [agents_j]

        if attributes is None:
            # if no specific attributes were given, take all of them
            attributes = list(network.nodes[agent_i].keys())

        # variable to return at the end of function
        success = False

        influenced_feature = random.choice(attributes)

        if regime != "many-to-one": # it must be "one-to-one" or "one-to-many"
            for neighbor in agents_j:
                # calculate 'opinion' distance on the trait that will be changed
                feature_difference = network.nodes[agent_i][influenced_feature] - \
                                     network.nodes[neighbor][influenced_feature]
                # influence function
                network.nodes[neighbor][influenced_feature] = network.nodes[neighbor][influenced_feature] + \
                    convergence_rate * (1 - homophily * abs(network.edges[agent_i, neighbor]["dist"])) * \
                    feature_difference
                # bounding the opinions to the pre-supposed opinion scale [0,1]
                if network.nodes[neighbor][influenced_feature] > feature_bounds['max']: network.nodes[neighbor][influenced_feature] = feature_bounds['max']
                if network.nodes[neighbor][influenced_feature] < feature_bounds['min']: network.nodes[neighbor][influenced_feature] = feature_bounds['min']

                if bi_directional == True and regime == "one-to-one":
                    # influence function applied again
                    # (note that feature_difference has not been updated after changing neighbor's feature)
                    network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][influenced_feature] - \
                        convergence_rate * (1 - homophily * abs(network.edges[agent_i, neighbor]["dist"])) * \
                        feature_difference
                    update_dissimilarity(network, [agent_i, neighbor], dissimilarity_measure, **kwargs)
                else:
                    update_dissimilarity(network, [neighbor], dissimilarity_measure, **kwargs)
                success = True

        else: # applies "many-to-one"
            set_of_influencers = [neighbor for neighbor in agents_j]
            
            if len(set_of_influencers) != 0:
                ## Calculate total influence as average of influence from all neighbors
                influence_values = []
                for neighbor in set_of_influencers:
                    # calculate feature distance on the feature that will be changed
                    feature_difference = network.nodes[neighbor][influenced_feature] - \
                                         network.nodes[agent_i][influenced_feature]

                    # calculate influence
                    influence_values.append(convergence_rate * (1 - homophily * abs(network.edges[agent_i, neighbor]["dist"])) * \
                        feature_difference)
                
                overall_influence = sum(influence_values) / len(influence_values)
                network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][influenced_feature] + overall_influence
                
                # bounding the opinions to the pre-supposed opinion scale 
                if network.nodes[agent_i][influenced_feature] > feature_bounds['max']: network.nodes[agent_i][influenced_feature] = feature_bounds['max']
                if network.nodes[agent_i][influenced_feature] < feature_bounds['min']: network.nodes[agent_i][influenced_feature] = feature_bounds['min']                    
                
                update_dissimilarity(network, [agent_i], dissimilarity_measure, **kwargs)
                success = True

        return success
