import defSim as ds
from defSim.Simulation import Simulation
from defSim.Experiment import Experiment
import pandas as pd
import numpy as np
import networkx as nx
import timeit
import os

# Implementing an output reporter which calculates polarization at the end of each run
## Output reporters are implemented based on the OutputTableCreator base class https://github.com/marijnkeijzer/defSim/blob/master/defSim/tools/CreateOutputTable.py
## Every output reporter should implement a static method called 'create_output', which calculates and returns the desired output
## Examples: https://github.com/marijnkeijzer/defSim/blob/master/defSim/tools/OutputMeasures.py

class PolarizationReporter(ds.tools.CreateOutputTable.OutputTableCreator):
    @staticmethod
    def create_output(network: nx.Graph, **kwargs):
        """
        Will calculate polarization for a given network.
        Polarization is based on the observed variance in opinion distances. 
        Opinion distances are drawn from the network, so they are based on whatever dissimilarity measure was 
        selected during the simulation.
        
        :param network: A networkx graph on which to calculate polarization
        :return: A single value for polarization, between 0 and 1.
        """

        distances = list(nx.get_edge_attributes(network, 'dist').values())

        return np.var(distances_pos_neg)
        

experiment = Experiment(
                    topology = 'grid',
                    attributes_initializer="random_continuous",
                    focal_agent_selector = 'random',
                    neighbor_selector = 'random',                           
                    influence_function = 'weighted_linear',
                    dissimilarity_measure="euclidean",                           
                    stop_condition = 'max_iteration',                           
                    max_iterations=25000,
                    communication_regime = 'one-to-one',
                    influence_parameters={
                       'homophily': [1, 2]
                       },
                    output_realizations = [],
                    repetitions=1
                )


results = experiment.run()
print(results)