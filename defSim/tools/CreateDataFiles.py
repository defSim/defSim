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
        # try to convert any 'object' columns to appropriate types
        output_table = output_table.convert_dtypes()
        # convert any int64 to int32
        columns_to_convert = list(output_table.select_dtypes(include=['int64']).columns)
        for column in columns_to_convert:
            output_table[column] = output_table[column].astype(int)
        # convert string to str
        columns_to_convert = list(output_table.select_dtypes(include=['string']).columns)
        for column in columns_to_convert:
            output_table[column] = output_table[column].astype(str)
        # coerce unconverted data types to str     
        columns_to_convert = list(output_table.select_dtypes(include=['object']).columns)
        for column in columns_to_convert:
            output_table[column] = output_table[column].astype(str)      

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


def unpack_tickwise_column(tickwise_column):
    """
    This function turns a column containing tickwise data into its own dataframe. 
    In output from simulations, columns of tickwise data contain a list of lists.
    Each sub-list represents values from one tick.

    :param tickwise_column: Pandas dataframe consisting of a single column with tickwise data.

    :returns: Unpacked version of this column where columns represent values and rows represent
        ticks. If the original columns contained multiple rows, a dataframe is returned for 
        each row.
    """

    output_dataframes = {}

    for index, row in tickwise_column.iterrows():
        output_dataframes[index] = pd.DataFrame(row[0])

    return output_dataframes


def create_tickwise_files(tickwise_dataframes, output_folder: Path, realization: DataFileCreator, **kwargs):
    """
    This function takes a dictionary of tickwise dataframes and stores them in files indexed by
    name of the tickwise column and simulation number.

    :param tickwise_dataframes: Dictionary containing dataframes indexed first by 
        column name and then by simulation number.
    :param output_folder = pathlib.Path: Path to folder where output files are stored.
    :param realization: DataFileCreator to apply to each dataframe. Set output path on initialization
        of the DataFileCreator instance.
    """

    for column_name, rows in tickwise_dataframes.items():
        for row_index, row_data in rows.items():
            output_path = output_folder / 'outputfile_{}_{}'.format(column_name, row_index)
            realization.create_file(output_table = row_data, output_path = output_path, **kwargs)



def create_data_files(output_table: pd.DataFrame, realizations: List[str or DataFileCreator]=[], output_folder_path: str or Path = None, **kwargs):
    """
    This function works as a factory method for the DataFileCreator component.
    It calls the create_file function of a specific implementation of the DataFileCreator and passes to it
    the kwargs dictionary.

    :param realizations: A list of output data file types, by name for file types implemented by default
        and as classes or instances for custom types.

    :returns: 
    """

    # set output path, create directory if it does not exist
    if output_folder_path is not None:
        output_folder = Path(output_folder_path).resolve()
    else:
        output_folder = Path('.', 'output').resolve() 
    if not output_folder.exists():
        output_folder.mkdir(parents = True)
    output_path = output_folder / 'outputfile'

    print("OUTPUT PATH SET: ", output_folder)

    # separate tickwise columns
    columns = list(output_table.columns)
    print("ALL COLUMNS ", columns)
    tickwise_columns = [column for column in columns if column.startswith('Tickwise_')]
    print("TICKWISE COLUMNS ", tickwise_columns)
    tickwise_output_table = output_table.filter(tickwise_columns, axis = 'columns')
    output_table = output_table.drop(tickwise_columns, axis = 'columns')

    # unpack tickwise data
    tickwise_dataframes = {}
    for column in tickwise_columns:
        tickwise_dataframes[column] = unpack_tickwise_column(tickwise_output_table[[column]])

    # set all string realizations to lowercase, keep all non-strings
    realizations = [realization.lower() if isinstance(realization, str) else realization for realization in realizations]

    if "pickle" in realizations:
        PickleFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)
        create_tickwise_files(tickwise_dataframes = tickwise_dataframes, output_folder = output_folder, realization = PickleFileCreator(), **kwargs)

    if "csv" in realizations:
        CSVFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)
        create_tickwise_files(tickwise_dataframes = tickwise_dataframes, output_folder = output_folder, realization = CSVFileCreator(), **kwargs)

    if any([i in realizations for i in ["hdf", "hdf5"]]):
        HDF5FileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)
        create_tickwise_files(tickwise_dataframes = tickwise_dataframes, output_folder = output_folder, realization = HDF5FileCreator(), **kwargs)

    if any([i in realizations for i in ["excel", "xlsx"]]):
        ExcelFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)
        create_tickwise_files(tickwise_dataframes = tickwise_dataframes, output_folder = output_folder, realization = ExcelFileCreator(), **kwargs)

    if "json" in realizations:
        JsonFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)
        create_tickwise_files(tickwise_dataframes = tickwise_dataframes, output_folder = output_folder, realization = JsonFileCreator(), **kwargs)

    if any([i in realizations for i in ["stata", "dta"]]):
        StataFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)
        create_tickwise_files(tickwise_dataframes = tickwise_dataframes, output_folder = output_folder, realization = StataFileCreator(), **kwargs)

    if any([i in realizations for i in ["markdown", "md"]]):
        MarkdownFileCreator().create_file(output_table = output_table, output_path = output_path, **kwargs)
        create_tickwise_files(tickwise_dataframes = tickwise_dataframes, output_folder = output_folder, realization = MarkdownFileCreator(), **kwargs)