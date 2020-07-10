from defSim.network_init import network_init
from defSim.agents_init import agents_init
from defSim.dissimilarity_component.HammingDistance import HammingDistance
from defSim.tools import NetworkDistanceUpdater
import networkx.algorithms.isomorphism as iso
import timeit
import random

random.seed("random")
network = network_init.generate_network("grid")
agents_init.initialize_attributes(network, "random_categorical")
network_comparison = network.copy()
HammingDistance().calculate_dissimilarity_networkwide(network)

all_attributes = network.nodes[1].keys()
def test_isomorphic():
    for i in range(10000):
        nm = iso.categorical_node_match(all_attributes, [0 for i in range(len(all_attributes))])

print("10000 isomorphism checks")
print("Time: "+str(timeit.timeit(test_isomorphic, number=1)))

def test_dissimilarity_check():
    for i in range(10000):
        NetworkDistanceUpdater.check_dissimilarity(network,0)

print("10000 dissimilarity checks")
print("Time: "+str(timeit.timeit(test_dissimilarity_check, number=1)))
