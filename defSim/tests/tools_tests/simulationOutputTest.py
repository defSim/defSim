from defSim.Simulation import Simulation
from defSim.Experiment import Experiment
from defSim.tools.CreateOutputTable import OutputTableCreator
import pandas as pd
import numpy as np
import timeit
import os

class TestCustomOutput(OutputTableCreator):
    @staticmethod
    def create_output(**kwargs):
        return "CustomOutput"

## Standard output
simulation = Simulation(topology="grid", influence_function="axelrod", stop_condition="strict_convergence",
                        communication_regime="one-to-one", parameter_dict={"num_agents": 225,
                                                                           "neighborhood": "von_neumann",
                                                                           "num_features": 7,
                                                                           "num_traits": 15},
                        max_iterations=100)
results = simulation.run()
with open("output_test.csv", "w+") as output_file:
    results.to_csv(output_file, sep=";", index=False)
print("results written to: %s" % os.path.abspath("output_test.csv"))

## Tickwise output
simulation = Simulation(topology="grid", influence_function="axelrod", stop_condition="strict_convergence",
                        communication_regime="one-to-one", parameter_dict={"num_agents": 225,
                                                                           "neighborhood": "von_neumann",
                                                                           "num_features": 7,
                                                                           "num_traits": 15},
                        tickwise = ['Isolates', TestCustomOutput, 'f02'],
                        max_iterations=100)
results = simulation.run()
with open("tickwise_output_test.csv", "w+") as output_file:
    results.to_csv(output_file, sep=";", index=False)
print("results written to: %s" % os.path.abspath("output_test.csv"))