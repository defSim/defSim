from defSim import Simulation, Experiment

sim1 = Simulation(seed = 1)
sim2 = Simulation(seed = 2)
sim3 = Simulation(seed = 3)
sim4 = Simulation(seed = 4)
sim5 = Simulation(seed = 5)
sim6 = Simulation(seed = 6)
sim7 = Simulation(seed = 7)

exp = Experiment(simulations = [sim1, sim2, sim3, sim4, sim5, sim6, sim7])

print("Estimating runtime")
print(exp.estimate_runtime())
print("Run experiment single")
print(exp.run())
print("Run experiment multicore")
print(exp.run(parallel = True))

sim11 = Simulation(seed = 11)
sim21 = Simulation(seed = 21)
sim31 = Simulation(seed = 31)
sim41 = Simulation(seed = 41)
sim51 = Simulation(seed = 51)
sim61 = Simulation(seed = 61)
sim71 = Simulation(seed = 71)

exp = Experiment(simulations = [sim1, sim2, sim3, sim4, sim5, sim6, sim7, sim11, sim21, sim31, sim41, sim51, sim61, sim71])

print("Run experiment multicore")
print(exp.run(parallel = True, num_cores = 2))