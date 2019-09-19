from defSim.focal_agent_sim import focal_agent_sim
from defSim.neighbor_selector_sim import neighbor_selector_sim
from defSim.tools import NetworkDistanceUpdater
from defSim.agents_init import agents_init
from defSim.network_init import network_init
from defSim.dissimilarity_component.HammingDistance import HammingDistance


# User wants to create their own network, change its transitivity manually, and then use it for their own experiment
# where they use a custom influence function
def changeTransitivity(network):
    return network


network = network_init.generate_network("grid", **{"num_agents": 100})
network = changeTransitivity(network)
agents_init.initialize_attributes(network, "random", **{"num_features": 3, "num_traits": 5})
HammingDistance.calculate_dissimilarity_networkwide(network)
agentIDs = list(network)

t = 0
while 1:
    t = t + 1
    # one simulation step
    selected_agent = focal_agent_sim.select_focal_agent(network, "random", agentIDs)
    neighbors = neighbor_selector_sim.select_neighbors(network, "random", selected_agent,
                                                            "one-to-one")
    myInfluenceFunction.spread_influence(network, neighbors, selected_agent, "one-to-one", "hamming")

    if t == 1000000: # max iteration
        print(t)
        break
    if not NetworkDistanceUpdater.check_dissimilarity(network, 0.1):
        print(t)
        break


