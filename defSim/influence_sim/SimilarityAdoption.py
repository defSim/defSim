import random

import networkx as nx
from .influence_sim import InfluenceOperator
from ..tools.NetworkDistanceUpdater import update_dissimilarity
from typing import List
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator



class SimilarityAdoption(InfluenceOperator):
    """
    Implements the InfluenceOperator in a way that recreates the original Axelrod experiment.
    """

    @staticmethod
    def spread_influence(network: nx.Graph, agent_i: int, agents_j: List[int] or int,
                         regime: str, dissimilarity_measure: DissimilarityCalculator, attributes: List[str] = None, **kwargs) -> bool:
        """
        In the influence function as Axelrod modeled it
        agents are more likely to influence each other if they are more similar. If an agent successfully influences one
        or more agents, the influenced agents adopt one feature on which they disagreed from the influencing agent.
        In the case of many-to-one communication, the influenced agent adopts the mode value of a feature on which there 
        is no consensus among the influencing agents.


        :param network: The network in which the agents exist.
        :param agent_i: the index of the focal agent that is either the source or the target of the influence
        :param agents_j: A list of indices of the agents who can be either the source or the targets of the influence. The list can have a
            single entry, implementing one-to-one communication.
        :param attributes: A list of the names of all the attributes that are subject to influence. If an agent has
            e.g. the attributes "Sex" and "Music taste", only supply ["Music taste"] as a parameter for this function.
            The influence function itself can still be a function of the "Sex" attribute.
        :param regime: Either "one-to-one", "one-to-many" or "many-to-one"
        :param dissimilarity_measure: An instance of a :class:`~defSim.dissimilarity_component.DissimilarityCalculator.DissimilarityCalculator`.
        :param kwargs: Additional parameters specific to the implementation of the InfluenceOperator.
            Possible parameters are the following:
        :param float=0 homophily: A number :math:`>` 0 that controls the shape of the influence curve.
            At 1, homophily is linear, like in Axelrod (1997)
            When the value for homophily :math:`>` 1, agents prefer similar agents more and more.
            When 0 :math:`<` homophily :math:`<` 1, agents have less of a preference for more similar neighbors.
            However, the values for the probability of successful influence will always be the same at 0, .5, and 1
            overlap. Respectively: 0, .5 and 1.
        :returns: true if agent(s) were successfully influenced
        """
        # todo: insert reference to Axelrod
        # todo: explain the homophily parameter

        if type(agents_j) != list:
            agents_j = [agents_j]
        homophily = kwargs.get("homophily", 1)

        success = False

        if attributes is None:
            # if no specific attributes were given, take all of them
            attributes = list(network.nodes[agent_i].keys())

        if regime != "many-to-one":
            incongruent_features = []
            for neighbor in agents_j:
                #todo this will fail in a global communication regime
                if network.edges[agent_i, neighbor]['dist'] < 1:
                    for feature in attributes:
                        if network.nodes[agent_i][feature] != network.nodes[neighbor][feature]:
                            if feature not in incongruent_features: incongruent_features.append(
                                feature)  # append the feature name if they are not the same
            if len(incongruent_features) == 0:
                return False
            else:
                influenced_feature = random.choice(incongruent_features)
                for neighbor in agents_j:
                    if network.edges[agent_i, neighbor]['dist'] >= .5:
                        p_infl_success = (
                                (1 / 2) ** (1 - homophily) * (1 - network.edges[agent_i, neighbor]['dist']) ** homophily)
                    else:
                        p_infl_success = (1 - (1 / 2) ** (1 - homophily) * (
                                1 - (1 - network.edges[agent_i, neighbor]['dist'])) ** homophily)
                    if random.uniform(0, 1) < p_infl_success:
                        success = True
                        network.nodes[neighbor][influenced_feature] = network.nodes[agent_i][influenced_feature]
                        update_dissimilarity(network, [neighbor], dissimilarity_measure, **kwargs)
        else:
            close_neighbors = []
            for neighbor in agents_j:
                if network.edges[agent_i, neighbor]['dist'] >= .5:
                    p_infl_success = (
                                (1 / 2) ** (1 - homophily) * (1 - network.edges[agent_i, neighbor]['dist']) ** homophily)
                else:
                    p_infl_success = (1 - (1 / 2) ** (1 - homophily) * (
                                1 - (1 - network.edges[agent_i, neighbor]['dist'])) ** homophily)
                #todo comment and improve time
                if random.uniform(0, 1) < p_infl_success:
                    close_neighbors.append(neighbor)
            incongruent_features = [] # [feature for feature in attributes if network.nodes[agent1]]
            incongruent_feature_values =[]
            for feature in attributes:
                neighbors_features = [value for key, value in nx.get_node_attributes(network, feature).items() if key in close_neighbors]
                # if len(set(neighbors_features))is one there is consensus
                if len(set(neighbors_features))!=1 and len(neighbors_features)!=0:
                    incongruent_features.append(feature)
                    # max(neighbors_features, key=neighbors_features.count) calculates the mode
                    incongruent_feature_values.append(max(neighbors_features, key=neighbors_features.count))
            if len(incongruent_features) != 0: # if the list is not empty
                influenced_featureID = random.choice([i for i in range(len(incongruent_features))])
                # if the focal agent does not already
                if network.nodes[agent_i][incongruent_features[influenced_featureID]] != incongruent_feature_values[influenced_featureID]:
                    success = True
                    network.nodes[agent_i][incongruent_features[influenced_featureID]] = incongruent_feature_values[influenced_featureID]
                    update_dissimilarity(network, [agent_i], dissimilarity_measure, **kwargs)

        return success