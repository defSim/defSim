from defSim.tools.CreateDataFiles import create_data_files
from defSim import Simulation, Experiment
import pandas as pd
import numpy as np
from unittest import TestCase


class TestCreatedataFiles(TestCase):

    def setUp(self):
        self.test_data_frame = pd.DataFrame.from_dict({'test': [1, 2, 3]})

    def test_file_creation(self):
        # create once (if no excel writer is installed, skip excel)
        try:
            create_data_files(output_table = self.test_data_frame, realizations = ['pickle', 'csv', 'excel', 'json', 'stata', 'markdown'])
        except ImportError:
            # also skip markdown if tabulate is not installed
            try:
                create_data_files(output_table = self.test_data_frame, realizations = ['pickle', 'csv', 'json', 'stata', 'markdown'])
            except ImportError:
                create_data_files(output_table = self.test_data_frame, realizations = ['pickle', 'csv', 'json', 'stata'])

        # check that hdf is marked as not yet implemented
        with self.assertRaises(NotImplementedError):
            create_data_files(output_table = self.test_data_frame, realizations = ['hdf'])

        # overwrite
        create_data_files(output_table = pd.DataFrame.from_dict({'test': [3, 4, 5]}), realizations = ['pickle', 'json'])

class TestCreateDataFilesWithSimData(TestCase):

    def setUp(self):
        self.sim = Simulation()

    def test_file_creation(self):
        # run simulation
        output_data = self.sim.run_simulation()

        # create (if no excel writer is installed, skip excel)
        try:
            create_data_files(output_table = output_data, realizations = ['pickle', 'csv', 'excel', 'json', 'stata', 'markdown'])
        except ImportError:
            # also skip markdown if tabulate is not installed
            try:
                create_data_files(output_table = output_data, realizations = ['pickle', 'csv', 'json', 'stata', 'markdown'])
            except ImportError:
                create_data_files(output_table = output_data, realizations = ['pickle', 'csv', 'json', 'stata'])

        # check that hdf is marked as not yet implemented
        with self.assertRaises(NotImplementedError):
            create_data_files(output_table = output_data, realizations = ['hdf'])

    def test_file_creation_from_sim(self):
        self.sim = Simulation(output_folder_path = "./output/fromsim", output_file_types = ['pickle', 'csv', 'json', 'stata'], tickwise = ['f01'])
        self.sim.run_simulation()

class TestCreateDataFilesWithExperimentData(TestCase):
    def test_file_creation(self):
        experiment = Experiment(output_folder_path = "./output/fromexperiment", output_file_types = ['pickle', 'csv', 'json', 'stata'], tickwise = ['f01'], attribute_parameters = {'num_features': [1, 2]})
        experiment.run()