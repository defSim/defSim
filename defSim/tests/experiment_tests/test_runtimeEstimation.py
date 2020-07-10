from defSim.Simulation import Simulation
from defSim.Experiment import Experiment
import random
import timeit
import datetime

experiment1 = Experiment(
                        topology = "ring",
                        attributes_initializer = "random_continuous",
                        attribute_parameters = {'num_features': [1, 2, 3, 4, 5, 6]},
                        influence_function = 'weighted_linear',
                        dissimilarity_measure = 'euclidean',
                        stop_condition = 'max_iteration',
                        max_iterations = 3000,
                        communication_regime = 'one-to-one',
                        influence_parameters = {'homophily': [0, 1, 2]},
                        repetitions = 5)

print("Runtime estimate 1 - default parameters: {} seconds".format(experiment1.estimate_runtime()))

print("Runtime estimate 2 - 10 sampled runs: {} seconds".format(experiment1.estimate_runtime(sample_runs = 10)))

print("Runtime estimate 3 - 10 sampled runs, 100 steps per run: {} seconds".format(experiment1.estimate_runtime(sample_runs = 10, sample_steps = 100)))

print("Runtime estimate 4 - more runs than parameter combinations: {} seconds".format(experiment1.estimate_runtime(sample_runs = 9999999)))

print("Runtime estimate 5a - 100 steps per run: {} seconds".format(experiment1.estimate_runtime(sample_steps = 100)))

#print("Runtime estimate 5b - more steps than max_iterations: {} seconds".format(experiment1.estimate_runtime(sample_steps = 3005)))

print("Runtime estimate 6 - one step per run: {} seconds".format(experiment1.estimate_runtime(sample_steps = 1)))

start = datetime.datetime.now()
experiment1.run()
runtime = datetime.datetime.now() - start
print("Actual runtime Experiment 1: {}".format(runtime))

experiment2 = Experiment(
                        topology = "ring",
                        attributes_initializer = "random_continuous",
                        attribute_parameters = {'num_features': [1, 2, 3, 4, 5, 6]},
                        influence_function = 'weighted_linear',
                        dissimilarity_measure = 'euclidean',
                        stop_condition = 'pragmatic_convergence',
                        communication_regime = 'one-to-one',
                        influence_parameters = {'homophily': [0, 1, 2]},
                        repetitions = 5)

print("Runtime estimate 7 - Experiment 2 - stop condition not set to max_iteration: {} seconds".format(experiment2.estimate_runtime()))