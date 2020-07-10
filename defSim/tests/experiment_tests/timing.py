from defSim.network_init import network_init
from defSim.agents_init import agents_init
from defSim.focal_agent_sim import focal_agent_sim
from defSim.neighbor_selector_sim import neighbor_selector_sim
from defSim.influence_sim import influence_sim
from defSim.Simulation import Simulation
from defSim.Experiment import Experiment
from defSim.dissimilarity_component.HammingDistance import HammingDistance
import random
import timeit

def timeNetworkCreation49():
    for i in range(100):
        network = network_init.generate_network("grid", **{**{"neighborhood": "von_neumann"}})

def timeNetworkCreation1000():
        network = network_init.generate_network("grid", **{"num_agents": 1000000, "neighborhood": "von_neumann"})

#print("Creating 100 networks with 49 agents each takes %f seconds" %(timeit.timeit(timeNetworkCreation49, number=1)))
#print("Creating 100 networks with 1000 agents each takes %f seconds" %(timeit.timeit(timeNetworkCreation1000, number=1)))


def timeAttributeInitialization49():
    network = network_init.generate_network("grid")
    for i in range(100):
        agents_init.initialize_attributes(network, "random")

#network = NetworkBuilder.generate_network("grid", **{"num_agents": 5000})
def timeAttributeInitialization1000():
    for i in range(100):
        agents_init.initialize_attributes(network, "random")

# print("Initializing 100 networks with 49 agents each takes %f seconds" %(timeit.timeit(timeAttributeInitialization49, number=1)))
# print("Initializing 100 networks with 1000 agents each takes %f seconds" %(timeit.timeit(timeAttributeInitialization1000, number=1)))


network = network_init.generate_network("grid")
agents_init.initialize_attributes(network, "random_continuous", **{"num_features": 3})
all_attributes = network.node[1].keys()
HammingDistance.calculate_dissimilarity_networkwide(network)
agents = list(network)
def timeIterationStepOneToOne49():
    random.seed("random")
    for i in range(2000000):
        agentid= focal_agent_sim.select_focal_agent(network, "random", agents)
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-one")
        influence_sim.spread_influence(network, "axelrod", agentid, neighborsid, list(all_attributes), "one-to-one")

def timeIterationStepOneToMany49():
    random.seed("random")
    for i in range(200000):
        agentid= focal_agent_sim.select_focal_agent(network, "random", agents)
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-many")
        influence_sim.spread_influence(network, "axelrod", agentid, neighborsid, list(all_attributes), "one-to-many", HammingDistance())

def timeIterationStepManyToOne49():
    random.seed("random")
    for i in range(200000):
        agentid= focal_agent_sim.select_focal_agent(network, "random", agents)
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "many-to-one")
        influence_sim.spread_influence(network, "axelrod", agentid, neighborsid, list(all_attributes), "many-to-one")

#print("2000000 simulation steps in a network with 49 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeIterationStepOneToOne49, number=1)))
#print("200000 simulation steps in a network with 49 agents and one-to-many communication take %f seconds" %(timeit.timeit(timeIterationStepOneToMany49, number=1)))
#print("200000 simulation steps in a network with 49 agents and many-to-one communication take %f seconds" %(timeit.timeit(timeIterationStepManyToOne49, number=1)))

#network = NetworkBuilder.generate_network("grid", **{"num_agents": 5000})
#AttributesInitializer.initialize_attributes(network, "random")
#agents5000 = list(network)
def timeIterationStepOneToOne5000():
    all_attributes = network.node[1].keys()
    random.seed("random")
    for i in range(2000000):
        agentid= focal_agent_sim.select_focal_agent(network, "random", agents5000)
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-one")
        influence_sim.spread_influence(network, "axelrod", [agentid], neighborsid, list(all_attributes), "one-to-one")

def timeIterationStepOneToMany5000():
    all_attributes = network.node[1].keys()
    random.seed("random")
    for i in range(2000000):
        agentid= focal_agent_sim.select_focal_agent(network, "random", agents5000)
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-many")
        influence_sim.spread_influence(network, "axelrod", [agentid], neighborsid, list(all_attributes), "one-to-many")

#print("2000000 simulation steps in a network with 5000 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeIterationStepOneToOne5000, number=1)))
#print("2000000 simulation steps in a network with 5000 agents and one-to-many communication take %f seconds" %(timeit.timeit(timeIterationStepOneToMany5000, number=1)))

simulation49 = Simulation(topology="grid",influence_function="axelrod",stop_condition="max_iteration")
random.seed("random")
def timeSimulationOneToOne49():
    for i in range(100):
        simulation49.run_simulation()

simulation5000 = Simulation(topology="grid", influence_function="axelrod",stop_condition="max_iteration", parameter_dict={"num_agents":5000})
def timeSimulationOneToOne5000():
    for i in range(1):
        simulation5000.run_simulation()


#print("100 full simulation with a network with 49 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeSimulationOneToOne49, number=1)))
#print("1 full simulation with a network with 5000 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeSimulationOneToOne5000, number=1)))

simulation49 = Simulation(topology="grid", influence_function="stochasticOverlap", stop_condition="strict_convergence")
random.seed("random")
def timeSimulationOneToOne49():
    for i in range(100):
        simulation49.run_simulation()
random.seed("random")
simulation5000 = Simulation(topology="grid", influence_function="stochasticOverlap", stop_condition="strict_convergence", parameter_dict={"num_agents":5000})
def timeSimulationOneToOne5000():
    for i in range(1):
        simulation5000.run_simulation()

#print("100 full simulation with a network with 49 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeSimulationOneToOne49, number=1)))
#print("1 full simulation with a network with 5000 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeSimulationOneToOne5000, number=1)))


def timeIterationStepOneToOne49Overlap():
    network = network_init.generate_network("grid")
    agents_init.initialize_attributes(network, "random")
    all_attributes = network.node[1].keys()
    random.seed("random")
    for i in range(2000000):
        agentid= focal_agent_sim.select_focal_agent(network, "random")
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-one")
        influence_sim.spread_influence(network, "stochasticOverlap", agentid, neighborsid, list(all_attributes), "one-to-one")

def timeIterationStepOneToMany49Overlap():
    network = network_init.generate_network("grid")
    agents_init.initialize_attributes(network, "random")
    all_attributes = network.nodes[1].keys()
    random.seed("random")
    for i in range(2000000):
        agentid= focal_agent_sim.select_focal_agent(network, "random")
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-many")
        influence_sim.spread_influence(network, "stochasticOverlap", agentid, neighborsid, list(all_attributes), "one-to-many")

#print("2000000 simulation steps in a network with 49 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeIterationStepOneToOne49Overlap, number=1)))
#print("2000000 simulation steps in a network with 49 agents and one-to-many communication take %f seconds" %(timeit.timeit(timeIterationStepOneToMany49Overlap, number=1)))

simulation49 = Simulation(topology="grid", influence_function="stochasticOverlap", stop_condition="strict_convergence", communication_regime="one-to-many")
random.seed("random")
def timeSimulationOneToMany49():
    for i in range(100):
        simulation49.run_simulation()



simulation5000 = Simulation(topology="grid", influence_function="stochasticOverlap", stop_condition="strict_convergence", parameter_dict={"num_agents":5000},communication_regime="one-to-many")
def timeSimulationOneToMany5000():
    for i in range(1):
        simulation5000.run_simulation()

#print("100 full simulation with a network with 49 agents and one-to-many communication take %f seconds" %(timeit.timeit(timeSimulationOneToMany49, number=1)))
#print("1 full simulation with a network with 5000 agents and one-to-many communication take %f seconds" %(timeit.timeit(timeSimulationOneToMany5000, number=1)))


#network = NetworkBuilder.generate_network("grid", **{"num_agents": 5000})
#AttributesInitializer.initialize_attributes(network, "random")
def timeIterationStepOneToOne5000Overlap():
    all_attributes = network.nodes[1].keys()
    random.seed("random")
    for i in range(20000):
        agentid= focal_agent_sim.select_focal_agent(network, "random")
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-one")
        influence_sim.spread_influence(network, "stochasticOverlap", agentid, neighborsid, list(all_attributes), "one-to-one")

def timeIterationStepOneToMany5000Overlap():
    all_attributes = network.nodes[1].keys()
    random.seed("random")
    for i in range(20000):
        agentid= focal_agent_sim.select_focal_agent(network, "random")
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-many")
        influence_sim.spread_influence(network, "stochasticOverlap", agentid, neighborsid, list(all_attributes), "one-to-many")

#print("20000 simulation steps in a network with 5000 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeIterationStepOneToOne5000Overlap, number=1)))
#print("20000 simulation steps in a network with 5000 agents and one-to-many communication take %f seconds" %(timeit.timeit(timeIterationStepOneToMany5000Overlap, number=1)))


def timeIterationStepOneToOne9():
    network = network_init.generate_network("grid", **{"num_agents": 9})
    agents_init.initialize_attributes(network, "random")
    all_attributes = network.nodes[1].keys()
    random.seed("random")
    for i in range(2000000):
        agentid= focal_agent_sim.select_focal_agent(network, "random")
        neighborsid = neighbor_selector_sim.select_neighbors(network, "random", agentid, "one-to-one")
        influence_sim.spread_influence(network, "axelrod", [agentid], neighborsid, list(all_attributes), "one-to-one")
#print("2000000 simulation steps in a network with 9 agents and one-to-one communication take %f seconds" %(timeit.timeit(timeIterationStepOneToOne9, number=1)))


experiment = Experiment(repetitions=100, stop_condition="strict_convergence")
#print("100 simulations in a network with 49 agents and one-to-one communication take %f seconds" %(timeit.timeit(experiment.run, number=1)))

