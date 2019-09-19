from defSim.network_init import network_init
# from defSim.agents_init import AttributeModifierFactory
from defSim.focal_agent_sim import focal_agent_sim
# from defSim.neighbor_selector_sim import neighborSelectorFactory
# from defSim.influence_sim import InfluenceSpreaderFactory
# from defSim.Simulation import Simulation
# from defSim.Experiment import Experiment
import random
import timeit

# checking whether it takes longer to pick from a large list
list100 = [i for i in range(100)]
list5000 = [i for i in range(500000)]
def test100():
    for i in range(1000000):
        random.choice(list100)

def test5000():
    for i in range(1000000):
        random.choise(list5000)

print("2000000 choices from list of length 100 take %f seconds" %(timeit.timeit(test100, number=1)))
print("2000000 choices from list of length 5000 take %f seconds" %(timeit.timeit(test100, number=1)))



network49 = network_init.generate_network("grid")
for item, thingy in network49.nodes.items():
    print(item)
    print(thingy)
network5000 = network_init.generate_network("grid", **{"num_agents": 5000})
print(network49.edges().toList())
# checking whether the access to a single node takes longer in big networks
def testAccessSmall():
    for i in range(10000000):
        a = network49[1]

def testAccessLarge():
    for i in range(10000000):
        a = network5000[1]

#print("10000000 times accessing the small network takes %f seconds" % (timeit.timeit(testAccessSmall, number=1)))
#print("10000000 times accessing the large network takes %f seconds" % (timeit.timeit(testAccessLarge, number=1)))

# checking whether transforming the network to a list is a factor

def testListTransformationSmall():
    for i in range(10000000):
        a = list(network49.nodes)

def testListTransformationLarge():
    for i in range(1000000):
        a = list(network5000)

# print("10000000 times transforming the small network takes %f seconds" % (timeit.timeit(testListTransformationSmall, number=1)))
# print("10000000 times transforming the large network takes %f seconds" % (timeit.timeit(testListTransformationLarge, number=1)))


#Confirming finding
def testRandomSelectionSmall():
    for i in range(100000):
        agentid = focal_agent_sim.select_focal_agent(network49, "random")

def testRandomSelectionLarge():
    for i in range(100000):
        agentid = focal_agent_sim.select_focal_agent(network5000, "random")

#print("100000 times picking a random agent in the small network takes %f seconds" % (timeit.timeit(testRandomSelectionSmall, number=1)))
#print("100000 times picking a random agent in the large network takes %f seconds" % (timeit.timeit(testRandomSelectionLarge, number=1)))

def testManualConversionSmall():
    for i in range(1000000):
        listy = [index for index,_ in network49.nodes().items()]

def testManualConversionLarge():
    for i in range(1000000):
        listy = [index for index,_ in network5000.nodes().items()]

#print("100000 times converting the small network manually takes %f seconds" % (timeit.timeit(testManualConversionSmall, number=1)))
#print("100000 times converting the large network manually takes %f seconds" % (timeit.timeit(testManualConversionLarge, number=1)))

