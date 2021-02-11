import sys
from defSim.Simulation import Simulation
import multiprocessing as mp
import pandas as pd
import pickle
import os
import time


class parallelSimulation:
    """
    This class exists solely for the purpose of running a chunk of different parameter combinations in parallel on
    one machine. This script is called from the command line with 3 arguments.

    Args:
        The index of the chunk that this instance shall run.
        The path to the folder with the pickle files from which the Simulation parameters are read.
        The path to where the output shall be written.

    """
    def main(self):
        args = sys.argv
        index_of_chunk = int(args[1])
        pickles_path = args[2]
        output_path = args[3]
        with open(os.path.join(pickles_path, "chunk%d.p" % index_of_chunk), "rb") as parameterFile:
            meta_parameter_dict = pickle.load(parameterFile)
        self.network = meta_parameter_dict["network"]
        self.topology = meta_parameter_dict["topology"]
        self.initialization = meta_parameter_dict["initialization"]
        self.focal_agent_selector = meta_parameter_dict["focal_agent_selector"]
        self.neighbor_selector = meta_parameter_dict["neighbor_selector"]
        self.influence_function = meta_parameter_dict["influence_function"]
        self.influencable_attributes = meta_parameter_dict["influencable_attributes"]
        self.network_modifier = meta_parameter_dict["network_modifier"]
        self.dissimilarity_measure = meta_parameter_dict["dissimilarity_measure"]
        self.stop_condition = meta_parameter_dict["stop_condition"]
        self.max_iterations = meta_parameter_dict["max_iterations"]
        parameter_dicts = meta_parameter_dict["parameter_dicts"]

        pool = mp.Pool(mp.cpu_count())
        results = pool.map_async(self.create_and_run_simulation, parameter_dicts)
        pool.close()
        while 1:
            if results.ready():
                break
            remaining = results._number_left
            print("Waiting for", remaining, "tasks to complete...")
            time.sleep(2)
        pool.join()
        # return pd.concat(results.get())
        full_df = pd.concat(results.get())
        with open(os.path.join(output_path, "results_batch_%d.csv" % index_of_chunk), "w") as output_file:
            full_df.to_csv(output_file, sep=";", index=False)
        return ("output created in: %s" % os.path.join(output_path, "results_batch_%d" % index_of_chunk))

    def create_and_run_simulation(self, parameter_dict):
        simulation = Simulation(network=self.network,
                                topology=self.topology,
                                attributes_initializer=self.initialization,
                                focal_agent_selector=self.focal_agent_selector,
                                neighbor_selector=self.neighbor_selector,
                                influence_function=self.influence_function,
                                influenceable_attributes= self.influencable_attributes,
                                stop_condition=self.stop_condition,
                                max_iterations=self.max_iterations,
                                network_modifier= self.network_modifier,
                                dissimilarity_measure= self.dissimilarity_measure,
                                communication_regime=parameter_dict["communication_regime"],
                                parameter_dict=parameter_dict
                                )
        return simulation.run()


if __name__ == '__main__':
    simulation = parallelSimulation()
    print(simulation.main())
