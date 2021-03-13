import random

import networkx as nx
from defSim.influence_sim.influence_sim import InfluenceOperator
from defSim.tools.NetworkDistanceUpdater import update_dissimilarity
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator
from typing import List

import math


class Leviathan(InfluenceOperator):

    @staticmethod
    def spread_influence(network: nx.Graph, agent_i: int, agents_j: List[int] or int,
                         regime: str, dissimilarity_measure: DissimilarityCalculator, attributes: List[str] = None,
                         **kwargs) -> bool:
        """
        The Leviathan model combines processes of vanity and opinion propagation.
        Each agent has an opinion about herself and about each other agent.
        The model assume that how strongly agents influence each other is dependent on the hierarchy between them.
        During an interaction, the agents propagate their opinions about themselves and about other people they know.
        Moreover, each individual is subject to vanity : if her interlocutor seems to value her highly,
        then she increases her opinion about this interlocutor. On the contrary she tends to decrease her opinion
        about those who seem to undervalue her.
        The model only exist in the one-to-one communication regime, with a bi-directional influence.
        Based on [Deffuant2013]_

        :param network: The network in which the agents exist.
        :param agent_i: the index of the focal agent that is either the source or the target of the influence
        :param agents_j: A list of indices of the agents who can be either the source or the targets of the influence. The list can have a single entry, implementing one-to-one communication.
        :param regime: only "one-to-one" is managed.
        :param dissimilarity_measure: An instance of a :class:`~defSim.dissimilarity_component.DissimilarityCalculator.DissimilarityCalculator`.
        :param kwargs: Additional parameters specific to the implementation of the InfluenceOperator. Possible parameters are the following:
        :param float=0.3 sigma: ruling the slope of the logistic function determining the propagation coefficients.
        :param int=1 gossip:the number of gossip in the influence. The agent aj talk about that number of agents.
        :param float=0.1 noise: the noise in the influence. Correspond to a uniform random number between -noise and noise.
        :param float=0.3 vanity: ruling the intensity of the reward or punishment depending of aj opinion about ai.
        :param float=1 propagation: ruling the intensity of the opinion influence.
        :returns: true if agent(s) were successfully influenced (always)
        """
        try:
            sigma = kwargs["sigma"]
        except KeyError:
            sigma = 0.3
        try:
            gossip = kwargs["gossip"]
        except KeyError:
            gossip = 0
        try:
            noise = kwargs["noise"]
        except KeyError:
            noise = 0.1
        try:
            vanity = kwargs["vanity"]
        except KeyError:
            vanity = 0.3
        try:
            propagation = kwargs["propagation"]
        except KeyError:
            propagation = 1

        # initialize the opinions of agents if it is not done
        # each agent has an opinion about herself and about each other agent
        if (nx.get_node_attributes(network, "opinions") == dict()):
            opinions = dict()
            for i in list(network.nodes):
                opinions[i] = dict()
                for other in list(network.nodes):
                    opinions[i][other] = 0
            nx.set_node_attributes(network, opinions, 'opinions')

        # in case of one-to-one, j is only one agent, but we still want to iterate over it
        if type(agents_j) != list:
            agents_j = [agents_j]

        if attributes is None:
            # if no specific attributes were given, take all of them
            attributes = list(network.nodes[agent_i].keys())

        # whether influence was exerted
        if regime != "one-to-one":
            raise NameError('Only the regime "one-to-one" is managed by the leviathan model')
        else:
            for neighbor in agents_j:
                # agent_j influence agent_i and agent_i influence agent_j
                Leviathan.influence(network, agent_i, neighbor, noise, gossip, sigma, vanity, propagation)
                Leviathan.influence(network, neighbor, agent_i, noise, gossip, sigma, vanity, propagation)
                update_dissimilarity(network, [agent_i, neighbor], dissimilarity_measure)
        return True

    @staticmethod
    def influence(network: nx.Graph, ai: int, aj: int, noise: float, gossip: int, sigma: float, vanity: float,
                  propagation: float):
        """
        The method of influence of the Leviathan model, called in spread_influence. The agent aj influence the opinion of ai.

        :param network: The network in which the agents exist.
        :param ai: the index of the focal agent that is the target of the influence.
        :param aj: the index of the focal agent that is the source of the influence.
        :param attributes: A list of the names of all the attributes that are subject to influence. If an agent has
            e.g. the attributes "Sex" and "Music taste", only supply ["Music taste"] as a parameter for this function.
            The influence function itself can still be a function of the "Sex" attribute.
        :param noise: the noise in the influence. Correspond to a uniform random number between -noise and noise .
        :param gossip: the number of gossip in the influence. The agent aj talk about that number of agents.
        :param sigma: ruling the slope of the logistic function determining the propagation coefficients.
        :param vanity: ruling the intensity of the reward or punishment depending of aj opinion about ai.
        :param propagation: ruling the intensity of the opinion influence.
        """
        # p = propagation * 1 / (1+e^((opinion_ii-opinion_ij)/sigma))
        p = propagation * 1 / (
                    1 + math.exp((network.nodes[ai]["opinions"][ai] - network.nodes[ai]["opinions"][aj]) / sigma))
        # opinion_ii += p * (opinion_ji-opinion_ii)
        network.nodes[ai]["opinions"][ai] += p * (
                    network.nodes[aj]["opinions"][ai] - network.nodes[ai]["opinions"][ai] + random.uniform(-noise,
                                                                                                           noise))
        # the opinions are bounded between -1 and 1
        network.nodes[ai]["opinions"][ai] = min(max(-1, network.nodes[ai]["opinions"][ai]), 1)
        # opinion_ij += p * (opinion_jj-opinion_ij)
        network.nodes[ai]["opinions"][aj] += p * (
                    network.nodes[aj]["opinions"][aj] - network.nodes[ai]["opinions"][aj] + random.uniform(-noise,
                                                                                                           noise))
        network.nodes[ai]["opinions"][aj] = min(max(-1, network.nodes[ai]["opinions"][aj]), 1)
        # aj propagate her opinions about other people her knows (gossip)
        if gossip > 0:
            known = [n for n in network.neighbors(aj)]
            known.remove(ai)
            for k in range(min(gossip, len(known))):
                aq = random.choice(known)
                known.remove(aq)
                # opinion_iq += p * (opinion_jq-opinion_iq)
                network.nodes[ai]["opinions"][aq] += p * (
                            network.nodes[aj]["opinions"][aq] - network.nodes[ai]["opinions"][aq] + random.uniform(
                        -noise, noise))
                network.nodes[ai]["opinions"][aq] = min(max(-1, network.nodes[ai]["opinions"][aq]), 1)
        # opinion_ij += vanity * (opinion_ji-opinion_ii)
        network.nodes[ai]["opinions"][aj] += vanity * (
                    network.nodes[aj]["opinions"][ai] - network.nodes[ai]["opinions"][ai] + random.uniform(-noise,
                                                                                                           noise))
        network.nodes[ai]["opinions"][aj] = min(max(-1, network.nodes[ai]["opinions"][aj]), 1)

