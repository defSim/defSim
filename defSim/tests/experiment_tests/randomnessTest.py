from defSim import Simulation
from defSim import Experiment

print("### two simulations without random seed ###")
simulationA = Simulation.Simulation(topology="grid",
                                    influence_function="stochasticOverlap",
                                    stop_condition="strict_convergence")
simulationB = Simulation.Simulation(topology="grid",
                                    influence_function="stochasticOverlap",
                                    stop_condition="strict_convergence")
print(simulationA.run_simulation())
print(simulationB.run_simulation())

print("### two simulations with strict convergence and random seed ###")
simulation1 = Simulation.Simulation(topology="grid",
                                    influence_function="stochasticOverlap",
                                    stop_condition="strict_convergence",
                                    seed="random")
simulation2 = Simulation.Simulation(topology="grid",
                                    influence_function="stochasticOverlap",
                                    stop_condition="strict_convergence",
                                    seed="random")
print(simulation1.run_simulation())
print(simulation2.run_simulation())

print("### two simulations with pragmatic convergence and random seed, to test whether the two methods actually produce"
      " the same result ### ")
simulation3 = Simulation.Simulation(topology="grid",
                                    influence_function="stochasticOverlap",
                                    stop_condition="pragmatic_convergence",
                                    seed="random")
simulation4 = Simulation.Simulation(topology="grid",
                                    influence_function="stochasticOverlap",
                                    stop_condition="pragmatic_convergence",
                                    seed="random")
print(simulation3.run_simulation())
print(simulation4.run_simulation())

print("### Two experiments, each three repetitions, without seed ###")

experiment1 = Experiment.Experiment(stop_condition="strict_convergence", repetitions=3)
experiment2 = Experiment.Experiment(stop_condition="strict_convergence", repetitions=3)
print("### Two experiments, each three repetitions, with seed ###")
experiment3 = Experiment.Experiment(stop_condition="strict_convergence", repetitions=3, seed="random")
experiment4 = Experiment.Experiment(stop_condition="strict_convergence", repetitions=3, seed="random")
experiment3.run()
experiment4.run()

