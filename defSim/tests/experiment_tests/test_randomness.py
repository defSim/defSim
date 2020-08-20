from defSim import Simulation
from defSim import Experiment

print("### two simulations with fixed seed ###")
simulationA = Simulation(topology="grid",
                                    influence_function="axelrod",
                                    stop_condition="strict_convergence",
                                    seed = 888888)
simulationB = Simulation(topology="grid",
                                    influence_function="axelrod",
                                    stop_condition="strict_convergence",
                                    seed = 888888)
print(simulationA.run_simulation())
print(simulationB.run_simulation())

print("### two simulations with strict convergence and random seed ###")
simulation1 = Simulation(topology="grid",
                                    influence_function="axelrod",
                                    stop_condition="strict_convergence",
                                    seed=None)
simulation2 = Simulation(topology="grid",
                                    influence_function="axelrod",
                                    stop_condition="strict_convergence",
                                    seed=None)
print(simulation1.run_simulation())
print(simulation2.run_simulation())

print("### two simulations with pragmatic convergence and random seed, to test whether the two methods actually produce"
      " the same result ### ")
simulation3 = Simulation(topology="grid",
                                    influence_function="axelrod",
                                    stop_condition="pragmatic_convergence",
                                    seed=None)
simulation4 = Simulation(topology="grid",
                                    influence_function="axelrod",
                                    stop_condition="pragmatic_convergence",
                                    seed=None)
print(simulation3.run_simulation())
print(simulation4.run_simulation())

print("### Two experiments, each three repetitions, without seed ###")
experiment1 = Experiment(stop_condition="strict_convergence", repetitions=3)
experiment2 = Experiment(stop_condition="strict_convergence", repetitions=3)
print(experiment1.run())
print(experiment2.run())

print("### Two experiments, each three repetitions, with seed ###")
experiment3 = Experiment(stop_condition="strict_convergence", repetitions=3, seed=777777)
experiment4 = Experiment(stop_condition="strict_convergence", repetitions=3, seed=777777)
print(experiment3.run())
print(experiment4.run())

