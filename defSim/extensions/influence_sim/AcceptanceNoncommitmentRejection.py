import networkx as nx

from defSim.influence_sim.influence_sim import InfluenceOperator
from defSim.tools.NetworkDistanceUpdater import update_dissimilarity
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator

from typing import List
import warnings


class AcceptanceNoncommitmentRejection(InfluenceOperator):

    def __init__(self, regime: str, **kwargs):
        """
        :param regime: This string determines the mode in which the agents influence each other.
              In 'one-to-one' the focal agent influences one other agent, in 'one-to-many' multiple other
              agents and in 'many-to-one' the focal agent is influenced by multiple other agents in the network.      
        :param kwargs: Additional parameters specific to the implementation of the InfluenceOperator. Possible parameters are the following:
        :param float=0.5 convergence_rate: A number between 0 and 1 determining how much an agent adopts other agents features. If
            it is one, the influenced agent takes the value of the influencing agent. Passed as a kwargs argument. If influence is negative,
            this determines the rate at which agents move away from each other.
        :param float=0.33 acceptance_limit: Upper limit of dissimilarity for which positive influence is exerted
        :param float=0.67 rejection_limit: Lower limit of dissimilarity for which negative influence is exerted
        :param bool=False bi_directional: A boolean specifying whether influence is bi- or uni-directional.           
        """

        self.regime = regime

        # Get parameters from parameter dictionary, or set default values if missing
        try:
            self.convergence_rate = kwargs["convergence_rate"]
        except KeyError:
            warnings.warn("convergence_rate not specified, using default value 0.5")
            self.convergence_rate = 0.5
        
        try:
            self.acceptance_limit = kwargs["acceptance_limit"]
        except KeyError:
            warnings.warn("acceptance_limit not specified, using default value 0.5")
            self.acceptance_limit = 0.33
        
        try:
            self.rejection_limit = kwargs["rejection_limit"]
        except KeyError:
            warnings.warn("rejection_limit not specified, using default value 0.5")
            self.rejection_limit = 0.67

        if self.acceptance_limit > self.rejection_limit:
            raise ValueError('Acceptance limit cannot be higher than rejection limit')

        self.bi_directional = kwargs.get('bi_directional', False)


    def spread_influence(self, network: nx.Graph, agent_i: int, agents_j: List[int] or int,
                         dissimilarity_measure: DissimilarityCalculator, attributes: List[str] = None, **kwargs) -> bool:
        """
        This influence function implements an influence function proposed by [JagerAmblard2005]_. Under this influence function,
        agents have a zone of acceptance, a zone of noncommitment and a zone of rejection.
        Agents are positively influenced by others whose dissimilarity falls in the zone of acceptance, not influenced by others whose 
        dissimilarity falls in the zone of non-commitment and negatively influenced by others whose dissimilarity falls in the
        zone of rejection.

        The zones of acceptance and rejection are defined by parameters acceptance_limit and rejection_limit, with 
        acceptance_limit < rejection_limit enforced. Jager & Amblard (2005) define the model for one feature, where dissimilarity
        between agents i and j is abs(feature_value_i - feature_value_j). To extend the model to multiple features, we apply
        the thresholds to the total dissimilarity between the two agents across all features. 

        The rate of convergence/divergence is set using parameter convergence_rate. Convergence rate is applied as follows:
        In zone of acceptance, opinion change for agent i from interaction with agent j is convergence_rate * (feature_value_j - feature_value_i)
        In zone of rejection, opinion change for agent i from interaction with agent j is convergence_rate * (feature_value_i - feature_value_j)
        In zone of non-commitment there is no opinion change from interaction between agents i and j.

        Note: opinions in Jager & Amblard (2005) are drawn from a uniform distribution between [-1:1]. defSim uses [0:1]. Keep
        this in mind when specifying thresholds. 

        Note: Jager & Amblard (2005) mention the possibility of different thresholds for different agents. This is not
        implemented in this influence function.

        Note: Jager & Amblard (2005) implement one-to-one interaction. Rules for one-to-many and many-to-one are generalizations
        of the same principles.

        Note: Jager & Amblard (2005) implement influence as uni-directional (agent j influences agent i). Implementation here also 
        allows bi-directional influence. In one-to-one influence, agent i influences agent j to be consistent with other influence
        functions implemented in defSim.

        :param network: The network in which the agents exist.
        :param agent_i: the index of the focal agent that is either the source or the target of the influence
        :param agents_j: A list of indices of the agents who can be either the source or the targets of the influence. The list can have a
            single entry, implementing one-to-one communication.
        :param attributes: A list of the names of all the attributes that are subject to influence. If an agent has
            e.g. the attributes "Sex" and "Music taste", only supply ["Music taste"] as a parameter for this function.
            The influence function itself can still be a function of the "Sex" attribute.
        :param dissimilarity_measure: An instance of a :class:`~defSim.dissimilarity_component.DissimilarityCalculator.DissimilarityCalculator`.
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

        # influence one feature at a time
        influenced_feature = random.choice(attributes)

        if self.regime != "many-to-one":
            for neighbor in agents_j:
                # influence
                if network.edges[agent_i, neighbor]['dist'] < self.acceptance_limit:
                    # positive influence
                    success = True
                    # i - j (because i will influence j)
                    feature_difference = network.nodes[agent_i][influenced_feature] - network.nodes[neighbor][
                        influenced_feature]
                    # j_t+1 = j + convergence_rate * (i-j)
                    network.nodes[neighbor][influenced_feature] = network.nodes[neighbor][
                                                                      influenced_feature] + self.convergence_rate * feature_difference
                elif network.edges[agent_i, neighbor]['dist'] > self.rejection_limit:
                    # negative influence
                    success = True
                    # i - j (because i will influence j)
                    feature_difference = network.nodes[agent_i][influenced_feature] - network.nodes[neighbor][
                        influenced_feature]
                    # j_t+1 = j - convergence_rate * (i-j)
                    network.nodes[neighbor][influenced_feature] = network.nodes[neighbor][
                                                                      influenced_feature] - self.convergence_rate * feature_difference

                if self.bi_directional == True and self.regime == "one-to-one":
                    # reverse of the above
                    if network.edges[agent_i, neighbor]['dist'] < self.acceptance_limit:
                        # i_t+1 = i - convergence_rate * (i-j)
                        network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][
                                                                        influenced_feature] - self.convergence_rate * feature_difference
                    elif network.edges[agent_i, neighbor]['dist'] > self.rejection_limit:
                        # i_t+1 = i + convergence_rate * (i-j)
                        network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][
                                                                        influenced_feature] + self.convergence_rate * feature_difference
                    update_dissimilarity(network, [agent_i, neighbor], dissimilarity_measure, **kwargs)
                else:
                    update_dissimilarity(network, [neighbor], dissimilarity_measure, **kwargs)

        else:
            # many to one
            # positively influenced by average of neighbors under acceptance limit
            accepted_neighbors = [neighbor for neighbor in agents_j if
                                network.edges[agent_i, neighbor]['dist'] < self.acceptance_limit]
            if len(accepted_neighbors) != 0:
                success = True
                average_value = np.mean([network.nodes[neighbor][influenced_feature] for neighbor in accepted_neighbors])
                feature_difference = average_value - network.nodes[agent_i][influenced_feature]
                network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][
                                                                influenced_feature] + self.convergence_rate * feature_difference
                update_dissimilarity(network, [agent_i], dissimilarity_measure)

            # negatively influenced by average of neighbors above rejection limit
            rejected_neighbors = [neighbor for neighbor in agents_j if
                                network.edges[agent_i, neighbor]['dist'] > self.rejection_limit]
            if len(rejected_neighbors) != 0:
                success = True
                average_value = np.mean([network.nodes[neighbor][influenced_feature] for neighbor in rejected_neighbors])
                feature_difference = average_value - network.nodes[agent_i][influenced_feature]
                network.nodes[agent_i][influenced_feature] = network.nodes[agent_i][
                                                                influenced_feature] - self.convergence_rate * feature_difference
                update_dissimilarity(network, [agent_i], dissimilarity_measure)                               

        return success

