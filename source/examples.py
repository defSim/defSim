# creating an Experiment with the default values, which recreates the classic axelrod experiment conditions
# in this example we want to try all kinds of communication regimes 1000 times

# Alternative way to import the experiment:
# from defSim import Experiment
# experiment = Experiment()

import defSim

import networkx as nx
from typing import List
from defSim import dissimilarity_calculator

experiment = defSim.Experiment(communication_regime=["one-to-one", "one-to-many", "many-to-one"], repetitions=1000)
results = experiment.run()
print(results)

#creating a Simulation
simulation = defSim.Simulation()
results = simulation.run_simulation()
print(results)

# creating a Simulation with your own influence function and running it step by step
class my_influence_function(defSim.InfluenceOperator):

    @staticmethod
    def spread_influence(network: nx.Graph, agent_i: int, agents_j: List[int] or int, regime: str,
                         dissimilarity_measure: dissimilarity_calculator, attributes: List[str]=None, **kwargs) -> bool:
        # print("enter your implementation here")
        pass

simulation = defSim.Simulation(influence_function=my_influence_function())
simulation.initialize_simulation()
for i in range(100):
    simulation.run_simulation_step()
results = simulation.create_output_table()

# using the building blocks manually with the respective factory methods
# only the influence function is here used directly (just as an example to show how to import it, you could also use:
# defSim.InfluenceOperator.spread_influence(network, "axelrod", focal_agent,neighbors, "one-to-one", defSim.HammingDistance())
# instead of using the factory method you can alway import the classes directly from the respective module

from defSim.influence_sim.Axelrod import Axelrod # import the axelrod infuence function

network = defSim.generate_network("ring")
defSim.agents_init.initialize_attributes(network, realization="random_categorical")
calculator = defSim.dissimilarity_calculator.select_calculator("euclidean")
calculator.calculate_dissimilarity_networkwide(network)

for i in range(100):
    focal_agent = defSim.focal_agent_sim.select_focal_agent(network, "random")
    neighbors = defSim.neighbor_selector_sim.select_neighbors(network, "random", focal_agent, "one-to-one")
    Axelrod.spread_influence(network, focal_agent, neighbors, regime="one-to-one", dissimilarity_measure=defSim.HammingDistance())

results = defSim.OutputMeasures.ClusterFinder.create_output(network, cluster_dissimilarity_threshold=.99)
print(results)

# using the building blocks manually with your own influence function
network = defSim.generate_network("ring")
defSim.agents_init.initialize_attributes(network, realization="random_categorical")
calculator = defSim.dissimilarity_calculator.select_calculator("euclidean")
calculator.calculate_dissimilarity_networkwide(network)

for i in range(100):
    focal_agent = defSim.focal_agent_sim.select_focal_agent(network, "random")
    neighbors = defSim.neighbor_selector_sim.select_neighbors(network, "random", focal_agent, "one-to-one")
    my_influence_function.spread_influence(network, focal_agent, neighbors, regime="one-to-one",
                                           dissimilarity_measure=defSim.HammingDistance())

results = defSim.OutputMeasures.ClusterFinder.create_output(network, cluster_dissimilarity_threshold=.99)
print(results)