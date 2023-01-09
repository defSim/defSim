from defSim.tools.CreateDataFiles import create_data_files
from defSim import Simulation, Experiment
import pandas as pd
from unittest import TestCase


class TestCreateDataFiles(TestCase):

    def setUp(self):
        self.test_data_frame = pd.DataFrame.from_dict({'test': [1, 2, 3]})

    def test_file_creation(self):
        create_data_files(output_table=self.test_data_frame, output_file_name='testOutput.csv')
        create_data_files(output_table=self.test_data_frame, output_file_name='testOutput.pickle')
        create_data_files(output_table=self.test_data_frame, output_file_name='testOutput.json')
        create_data_files(output_table=self.test_data_frame, output_file_name='testOutput.stata')

        try:
            create_data_files(output_table=self.test_data_frame, output_file_name='testOutput.xlsx')
        except ImportError:
            pass  # no problem

        try:
            create_data_files(output_table=self.test_data_frame, output_file_name='testOutput.markdown')
        except ImportError:
            pass  # no problem: `tabulate' is not installed

        with self.assertRaises(NotImplementedError):  # check that hdf is marked as not yet implemented
            create_data_files(output_table=self.test_data_frame, output_file_name='testOutput.hdf')

        # overwrite
        create_data_files(output_table=pd.DataFrame.from_dict({'test': [3, 4, 5]}), output_file_name='testOutput.json')


class TestCreateDataFilesWithSimData(TestCase):

    def setUp(self):
        self.sim = Simulation(max_iterations=10)

    def test_file_creation(self):
        # run simulation
        output_data = self.sim.run()

        create_data_files(output_table=output_data, output_file_name='testOutput.csv')
        create_data_files(output_table=output_data, output_file_name='testOutput.pickle')
        create_data_files(output_table=output_data, output_file_name='testOutput.json')
        create_data_files(output_table=output_data, output_file_name='testOutput.stata')
        try:
            create_data_files(output_table=output_data, output_file_name='testOutput.xlsx')
        except ImportError:
            pass  # no problem
        try:
            create_data_files(output_table=output_data, output_file_name='testOutput.markdown')
        except ImportError:
            pass  # no problem: `tabulate' is not installed

        with self.assertRaises(NotImplementedError):  # check that hdf is marked as not yet implemented
            create_data_files(output_table=output_data, output_file_name='testOutput.hdf')

    def test_file_creation_from_sim(self):
        self.sim = Simulation(max_iterations=10,
                              output_folder_path="./output/from_sim",
                              output_file_name='testOutput.csv',
                              tickwise=['f01'])
        self.sim.run()


class TestCreateDataFilesWithExperimentData(TestCase):
    def test_file_creation(self):
        experiment = Experiment(max_iterations=10,
                                output_folder_path="./output/from_experiment",
                                output_file_name='testOutput.csv',
                                tickwise=['f01'],
                                attribute_parameters={'num_features': [1, 2]})
        experiment.run()
