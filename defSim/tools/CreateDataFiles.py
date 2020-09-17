import pandas as pd
from pathlib import Path
from typing import List
from abc import ABC, abstractmethod
import warnings

class DataFileCreator(ABC):
    """
    This class is responsible for creating data files from Pandas dataframes.
    Inherit from this class and implement the create_file method to generate the desired output file for the output table.
    """

    @abstractmethod
    def create_file(self, output_table: pd.DataFrame, output_path: str or pathlib.Path, **kwargs):
        """
        This method receives a Pandas DataFrame and generates an output file.

        :param output_table: A Pandas DataFrame.

        :returns:
        """

        pass


class PickleFileCreator(DataFileCreator):
    def create_file(self, output_table: pd.DataFrame, output_path: str or pathlib.Path, **kwargs):
        # file path for output type
        output_path = output_path.with_suffix('.pickle')
        # remove file if output file already exists at given path
        if output_path.exists():
            print("EXISTS")
            output_path.unlink()
        # create new output file
        output_table.to_pickle(path = output_path, **kwargs)


class CSVFileCreator(DataFileCreator):
    def create_file(self, output_table: pd.DataFrame, output_path: str or pathlib.Path, **kwargs):
        # file path for output type
        output_path = output_path.with_suffix('.csv')
        # remove file if output file already exists at given path
        if output_path.exists():
            output_path.unlink()
        # create new output file
        output_table.to_csv(path_or_buf = output_path, **kwargs)


class HDF5FileCreator(DataFileCreator):
    def create_file(self, output_table: pd.DataFrame, output_path: str or pathlib.Path, **kwargs):
        raise NotImplementedError
        # needs work on understanding how to best utilize this file format
        #output_table.to_hdf(path_or_buf = output_path.with_suffix('.hdf'), **kwargs)
        

class ExcelFileCreator(DataFileCreator):
    def create_file(self, output_table: pd.DataFrame, output_path: str or pathlib.Path, **kwargs):
        # file path for output type
        output_path = output_path.with_suffix('.xlsx')
        # remove file if output file already exists at given path
        if output_path.exists():
            output_path.unlink()

        # create new output file
        try:
            output_table.to_excel(excel_writer = output_path, **kwargs)
        except ImportError as e:
            try:
                output_table.to_excel(excel_writer = output_path, engine = 'xlsxwriter', **kwargs)
            except ImportError as e:
                raise ImportError("No Excel writer engine installed. Install either openpyxl or xlsxwriter.")
                


class JsonFileCreator(DataFileCreator):
    def create_file(self, output_table: pd.DataFrame, output_path: str or pathlib.Path, **kwargs):
        # file path for output type
        output_path = output_path.with_suffix('.json')
        # remove file if output file already exists at given path
        if output_path.exists():
            output_path.unlink()
        # create new output file
        output_table.to_json(path_or_buf = output_path, **kwargs)       


class StataFileCreator(DataFileCreator):
    def create_file(self, output_table: pd.DataFrame, output_path: str or pathlib.Path, **kwargs):
        # file path for output type
        output_path = output_path.with_suffix('.dta')
        # remove file if output file already exists at given path
        if output_path.exists():
            output_path.unlink()
        # create new output file
        output_table.to_stata(path = output_path, **kwargs)


class MarkdownFileCreator(DataFileCreator):
    def create_file(self, output_table: pd.DataFrame, output_path: str or pathlib.Path, **kwargs):
        # file path for output type
        output_path = output_path.with_suffix('.md')
        # remove file if output file already exists at given path
        if output_path.exists():
            output_path.unlink()
        # create new output file
        with open(output_path, 'w') as outfile:
            output_table.to_markdown(buf = outfile, **kwargs)


def create_data_files(output_table: pd.DataFrame, realizations: List[str or DataFileCreator]=[], **kwargs):
    """
    This function works as a factory method for the DataFileCreator component.
    It calls the create_file function of a specific implementation of the DataFileCreator and passes to it
    the kwargs dictionary.

    :param realizations: A list of output data file types, by name for file types implemented by default
        and as classes or instances for custom types.

    :returns: 
    """

    # set output path, create directory if it does not exist
    output_folder = Path('.', 'output').resolve() 
    if not output_folder.exists():
        output_folder.mkdir(parents = True)
    output_path = output_folder / 'outputfile'

    # set all string realizations to lowercase, keep all non-strings
    realizations = [realization.lower() if isinstance(realization, str) else realization for realization in realizations]

    if "pickle" in realizations:
        PickleFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)

    if "csv" in realizations:
        CSVFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)

    if any([i in realizations for i in ["hdf", "hdf5"]]):
        HDF5FileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)

    if any([i in realizations for i in ["excel", "xlsx"]]):
        ExcelFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)

    if "json" in realizations:
        JsonFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)

    if any([i in realizations for i in ["stata", "dta"]]):
        StataFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)

    if any([i in realizations for i in ["markdown", "md"]]):
        MarkdownFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)