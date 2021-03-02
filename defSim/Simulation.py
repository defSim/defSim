from tqdm import tqdm
from typing import List, Union
import inspect
import random
# math.inf imported here rather than explicit references to math.inf because it will be called repeatedly
# and having inf imported already is significantly faster
from math import inf
import warnings
import time
import pandas as pd
import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
from defSim.network_init import network_init
from defSim.agents_init import agents_init
from defSim.focal_agent_sim import focal_agent_sim
from defSim.neighbor_selector_sim import neighbor_selector_sim
from defSim.influence_sim import influence_sim
from defSim.network_evolution_sim import network_evolution_sim
from defSim.network_evolution_sim.network_evolution_sim import NetworkModifier
from defSim.network_evolution_sim.MaslovSneppenModifier import MaslovSneppenModifier
from defSim.tools import NetworkDistanceUpdater
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator
from defSim.dissimilarity_component.dissimilarity_calculator import select_calculator
from defSim.tools import OutputMeasures
from defSim.tools import CreateOutputTable
from defSim.tools.CreateDataFiles import DataFileCreator, create_data_files
from defSim.tools.ConvergenceChecks import ConvergenceCheck, PragmaticConvergenceCheck, OpinionDistanceConvergenceCheck


class Simulation:
    """
    This class is responsible for initializing and running a single experiment until the desired stop criterion is
    reached. The Simulation class contains three different stop criterion implementations as methods, but more can be
    added.
    The class is initialized in a similar way as the Experiment class but it does not accept multiple parameter
    values per parameter and also all optional parameters are passed in one combined dictionary.

    Args:
        network (str nx.Graph=None): A NetworkX object that was created (e.g. from empirical data) or "list". If "list", the network is read from the parameter dict under the 'network' parameter.
        topology (String = "grid"): Options are "grid", "ring" and "spatial_random_graph", or you could give the name of one of the generators included in the `NetworkX package <https://networkx.github.io/documentation/stable/reference/generators.html>`__..
        network_modifiers (NetworkModifier or List = None): A modifier or list of modifiers to apply to the network after initialization. Each modifier should be derived from the NetworkModifier base class.
        attributes_initializer (String = "random_categorical" or :class:`AttributesInitializer`): Either be a custom AttributesInitializer or a string that selects from the predefined choices: ["random_categorical", "random_continuous"...]
        focal_agent_selector (str = "random" or :class:`FocalAgentSelector`): Either a custom FocalAgentSelector or a string that selects from the predefined options ["random", ...]
        neighbor_selector (str = "random" or :class:`NeighborSelector`): Either a custom NeighborSelector or a string that selects from the predefined options ["random", "similar" ...}
        influence_function (str = "similarity_adoption" or :class:`InfluenceOperator`): Either a custom influence function or a string that selects from the predefined options ["similarity_adoption", "bounded_confidence", "weighted_linear", ...}
        influenceable_attributes (List = None): This is a list of the attribute names, that may be changed in the influence step
        dissimilarity_measure (String = "hamming" or :class:`DissimilarityCalculator`): Either a custom DissimilarityCalculator or a string that selects from the predefined options ["hamming", "euclidean", ...}
        stop_condition (str = "max_iteration"): Determines at what point a simulation is supposed to stop. Options include "strict_convergence", which means that it is theoretically not possible anymore for any agent to influence another, "pragmatic_convergence", which means that it is assumed that little change is possible anymore, and "max_iteration" which just stops the simulation after a certain amount of time steps.
        communication_regime (str = "one-to-one"): Options are "one-to-one", "one-to-many" and "many-to-one".
        parameter_dict: A dictionary with all parameters that will be passed to the specific component implementations.
        seed (str = None): A seed for stable replication
        output_realizations (list = [str or CreateOutputTable.OutputTableCreator]): This optional list should contain all output to generate at the end of each run, by name for defaults or as class inheriting from OutputTableCreator
        output_folder_path (str or pathlib.Path): If not None, the output table is saved to file(s) in this location. 
        output_file_types (List[str or DataFileCreator]): Determines which types of output files will be saved at output_folder_path. See tools.CreateDataFiles for options.
        tickwise (List = [str]):  A list of strings with the names of agent attributes that need to be recorded at every timestep
    """

    def __init__(self,
                 network=None,
                 topology: str = "grid",
                 network_modifiers: List[NetworkModifier] = None,
                 attributes_initializer: str = "random_categorical" or agents_init.AttributesInitializer,
                 focal_agent_selector: str = "random" or focal_agent_sim.FocalAgentSelector,
                 neighbor_selector: str = "random" or neighbor_selector_sim.NeighborSelector,
                 influence_function: str = "similarity_adoption" or influence_sim.InfluenceOperator,
                 influenceable_attributes: List = None,
                 dissimilarity_measure: str = "hamming" or DissimilarityCalculator,
                 stop_condition: str = "max_iteration" or ConvergenceCheck,
                 max_iterations: int = 100000,
                 communication_regime: str = "one-to-one",
                 parameter_dict={},
                 seed=None,
                 output_realizations=[],
                 output_folder_path: str or pathlib.Path = None,
                 output_file_types: List[str or DataFileCreator] = [],
                 tickwise: List[str] = []
                 ):
        self.network = network
        self.topology = topology
        self.network_modifiers = network_modifiers
        self.attributes_initializer = attributes_initializer
        self.focal_agent_selector = focal_agent_selector
        self.neighbor_selector = neighbor_selector
        self.influence_function = influence_function
        self.influenceable_attributes = influenceable_attributes
        self.communication_regime = communication_regime
        self.dissimilarity_calculator = dissimilarity_measure if isinstance(dissimilarity_measure,
                                                                            DissimilarityCalculator) else \
            select_calculator(dissimilarity_measure)
        self.stop_condition = stop_condition
        self.max_iterations = max_iterations
        self.parameter_dict = parameter_dict
        self.seed = seed
        self.network_provided = False if network is None else True
        self.agentIDs = []
        self.time_steps = 0
        self.influence_steps = 0  # counts the successful influence steps
        self.output_realizations = output_realizations
        self.output_folder_path = output_folder_path
        self.output_file_types = output_file_types
        self.tickwise = tickwise
        self.initialize_tickwise_output()

    def initialize_tickwise_output(self):
        if 'output_step_size' in self.parameter_dict.keys():
            self.tickwise_output_step_size = self.parameter_dict['output_step_size']
        else:
            self.tickwise_output_step_size = 1

        self.tickwise_output = {}
        for tickwise_realization in self.tickwise:
            if tickwise_realization in CreateOutputTable._implemented_output_realizations:
                self.tickwise_output['defaults'] = []
            else:
                if inspect.isclass(tickwise_realization) and issubclass(tickwise_realization,
                                                                        CreateOutputTable.OutputTableCreator):
                    tickwise_realization = tickwise_realization()
                if isinstance(tickwise_realization, CreateOutputTable.OutputTableCreator):
                    if tickwise_realization.label != "":
                        self.tickwise_output[tickwise_realization.label] = []
                    else:
                        tickwise_realization.label = "CustomOutput{}".format(random.randint(1000, 9999))
                        self.tickwise_output[tickwise_realization.label] = []
                else:
                    self.tickwise_output[tickwise_realization] = []

    def return_values(self) -> pd.DataFrame:
        """
        This method returns the values stored in the Simulation object. Both default, and user-specified values are
        returned to the console to make the Simulation object more transparent.

        :returns: A Pandas DataFrame with the parameter settings
        """

        parameter_df = pd.DataFrame()
        for i in self.__dict__.keys():
            if type(self.__dict__[i]) == dict:
                for key, val in self.__dict__[i].items():
                    parameter_df[key] = [val]
            else:
                parameter_df[i] = [self.__dict__[i]]

        return parameter_df

    def run(self, initialize: bool = True, show_progress: bool = True) -> pd.DataFrame:
        """
        This method initializes the network if none is given, initializes the attributes of the agents, and also
        computes and sets the distances between each neighbor.
        It then calls different functions that execute the simulation based on which stop criterion was selected.
        
        :param bool=True initialize: Initialize the simulation before running (disable if initialization was
            done separately)
        :param bool=True show_progress: Whether to show progress bar
        :returns: A Pandas DataFrame that contains one row of data. To see what output the output contains see
            :func:`~create_output_table`

        """
        if initialize:
            self.initialize()

        if self.influence_function == 'list':
            self.influence_function = self.parameter_dict['influence_function']

        if self.stop_condition == "pragmatic_convergence":
            self._run_until_pragmatic_convergence(show_progress)
        elif self.stop_condition == "strict_convergence":
            self._run_until_strict_convergence(show_progress)
        elif isinstance(self.stop_condition, ConvergenceCheck):
            self._run_until_convergence(show_progress)
        elif self.stop_condition == "max_iteration":
            self._run_until_max_iteration(show_progress)
        else:
            raise ValueError(
                "Can only select from the options ['pragmatic_convergence', 'strict_convergence', 'max_iteration'] or pass custom stop condition")

        return self.create_output_table()

    def run_simulation(self, initialize: bool = True) -> pd.DataFrame:
        """
        Will be deprecated in favor of Simulation.run().
        Replace in code, will be removed at or before v1.0.0
        """

        warnings.warn(
            "Simulation.run_simulation() is replaced by Simulation.run() and will be deprecated at or before defSim v1.0.0",
            category=FutureWarning)
        return self.run(initialize=initialize)

    def initialize(self):
        """
        This method initializes the network if none is given, applies network modifiers, initializes the attributes of the agents, 
        and also computes and sets the distances between each neighbor.
        """

        # reset steps
        self.time_steps = 0
        self.influence_steps = 0

        # reset tickwise output
        self.initialize_tickwise_output()

        if self.seed is None:
            self.seed = random.randint(10000, 99999)
        random.seed(self.seed)
        self.parameter_dict['np_random_generator'] = np.random.default_rng(self.seed)

        ## if deprecated ms_rewiring parameter is set in parameter dict, replace with network modifier
        if 'ms_rewiring' in list(self.parameter_dict.keys()):
            warnings.warn(
                "Setting ms_rewiring in parameter dict is deprecated. Pass an instance of MaslovSneppenModifier in network_modifiers instead.",
                DeprecationWarning)
            if self.network_modifiers is None:
                self.network_modifiers = [MaslovSneppenModifier(rewiring_prop=self.parameter_dict['ms_rewiring'])]
            else:
                self.network_modifiers.append(MaslovSneppenModifier(rewiring_prop=self.parameter_dict['ms_rewiring']))

                # read or generate network if no nx.Graph was provided, apply network modifiers
        if self.network_provided:
            if self.network == 'list':
                self.network = self.parameter_dict.pop('network')
            if not isinstance(self.network, nx.Graph) and self.network is not None:
                self.network = network_init.read_network(self.network)

            ## apply network modifiers
            if self.network_modifiers is not None:
                for modifier in self.network_modifiers:
                    modifier.rewire_network(network)
        else:
            self.network = network_init.generate_network(self.topology, network_modifiers=self.network_modifiers,
                                                         **self.parameter_dict)

            # storing the indices of the agents to access them quicker
        self.agentIDs = list(self.network)

        # initialize agent attributes (accepts string realizations and instances of AttributesInitializer classes)
        agents_init.initialize_attributes(self.network, self.attributes_initializer, **self.parameter_dict)

        # initialization of distances between neighbors
        self.dissimilarity_calculator.calculate_dissimilarity_networkwide(self.network)

    def initialize_simulation(self):
        """
        Will be deprecated in favor of Simulation.initialize().
        Replace in code, will be removed at or before v1.0.0
        """

        warnings.warn(
            "Simulation.initialize_simulation() is replaced by Simulation.initialize() and will be deprecated at or before defSim v1.0.0",
            category=FutureWarning)
        return self.initialize()

    def run_step(self):
        """
        Executes one iteration of the simulation step which includes the selection of a focal agent, the selection
        of the neighbors and the influence step.
        If the user passed their own implementations of those components, they will be called to execute these steps,
        otherwise the respective factory functions will be called.
        """

        selected_agent = focal_agent_sim.select_focal_agent(self.network, self.focal_agent_selector,
                                                            self.agentIDs, **self.parameter_dict)

        neighbors = neighbor_selector_sim.select_neighbors(self.network, self.neighbor_selector,
                                                           selected_agent,
                                                           self.communication_regime, **self.parameter_dict)

        success = influence_sim.spread_influence(self.network,
                                                 self.influence_function,
                                                 selected_agent,
                                                 neighbors,
                                                 self.communication_regime,
                                                 self.dissimilarity_calculator,
                                                 self.influenceable_attributes,
                                                 **self.parameter_dict)

        if self.tickwise and self.time_steps % self.tickwise_output_step_size == 0:  # list is not empty
            defaults_selected = [i for i in self.tickwise if i in CreateOutputTable._implemented_output_realizations]
            if len(defaults_selected) > 0:
                self.tickwise_output['defaults'].append(
                    CreateOutputTable.create_output_table(network=self.network, realizations=defaults_selected))
            for i in self.tickwise:
                if not i in defaults_selected:
                    if isinstance(i, CreateOutputTable.OutputTableCreator):
                        self.tickwise_output[i.label].append(i.create_output(network=self.network))
                    else:
                        self.tickwise_output[i].append(
                            OutputMeasures.AttributeReporter(feature=i).create_output(self.network))

        self.time_steps += 1
        if success:
            self.influence_steps += 1

    def run_simulation_step(self):
        """
        Will be deprecated in favor of Simulation.run_step().
        Replace in code, will be removed at or before v1.0.0
        """

        warnings.warn(
            "Simulation.run_simulation_step() is replaced by Simulation.run_step() and will be deprecated at or before defSim v1.0.0",
            category=FutureWarning)
        return self.run_step()

    def create_output_table(self) -> pd.DataFrame:
        """
        This method measures multiple characteristics of the network in its current state and writes them to a Pandas
        DataFrame. It contains the following columns:

            * Seed: The random seed that was used.
            * Topology: Which network topology was used.
            * Ticks: For how many iterations the simulation ran (so far).
            * SuccessfulInfluence: How often an agent was successfully influenced by another agent.
            * All basic columns included in :meth:`~defSim.tools.CreateOutputTable.create_output_table`

        Saves the output table to file(s) indicated by self.output_file_types if self.output_folder_path is not None.

        :returns: A Pandas DataFrame with one row.
        """

        parameter_settings = {'Seed': self.seed,
                              'Ticks': self.time_steps,
                              'SuccessfulInfluence': self.influence_steps}
        if self.network_provided:
            parameter_settings['Topology'] = "pre-loaded"
        else:
            parameter_settings['Topology'] = self.topology
        parameter_settings = {**parameter_settings, **self.parameter_dict}

        if self.output_realizations == []:
            self.output_realizations = ["Basic"]

        results = CreateOutputTable.create_output_table(network=self.network,
                                                        realizations=self.output_realizations,
                                                        settings_dict=parameter_settings,
                                                        tickwise_output=self.tickwise_output,
                                                        **self.parameter_dict)

        results_dataframe = pd.DataFrame.from_dict({k: [results[k]] for k in results.keys()})

        if self.output_folder_path is not None:
            create_data_files(output_table=results_dataframe, realizations=self.output_file_types,
                              output_folder_path=self.output_folder_path)

        return results_dataframe

    def _run_until_pragmatic_convergence(self, show_progress: bool = False):
        """
        Pragmatic convergence means that each "step_size" time steps it is checked whether the structure of the network
        and all attributes are still the same. If thats the case, it is assumed that the simulation converged and it stops.

        :param int=100 step_size: determines how often it should be checked for a change in the network.
        :param bool show_progress: bool determines whether to show progress bar
        """
        try:
            step_size = self.parameter_dict["step_size"]
        except KeyError:
            step_size = 100

        stop_condition = PragmaticConvergenceCheck(initial_network=self.network.copy())

        if show_progress:
            for _ in tqdm(range(self.max_iterations), mininterval=1):
                self.run_step()
                if self.time_steps % step_size == 0:
                    if stop_condition.check_convergence(self.network):
                        break
        else:
            for _ in range(self.max_iterations):
                self.run_step()
                if self.time_steps % step_size == 0:
                    if stop_condition.check_convergence(self.network):
                        break


    def _run_until_strict_convergence(self, show_progress: bool = False):
        """
        Here the convergence of the simulation is periodically checked by assessing the distance between each neighbor
        in the network. Unless there is no single pair left that can theoretically influence each other, the simulation
        continues.

        :param float=inf maximum: A value that determines above what maximum distance two agents can't influence each other anymore.
        :param float=inf minimum: A value that determines below what minimum distance two agents can't influence each other anymore.
        :param int=100 step_size: determines how often it should be checked for a change in the network.
        :param bool show_progress: bool determines whether to show progress bar
        """
        try:
            maximum = self.parameter_dict["convergence_dissimilarity_maximum"]
        except KeyError:
            maximum = inf
        try:
            minimum = self.parameter_dict["convergence_dissimilarity_minimum"]
        except KeyError:
            minimum = 0.0
        try:
            step_size = self.parameter_dict["step_size"]
        except KeyError:
            step_size = 100

        stop_condition = OpinionDistanceConvergenceCheck(maximum=maximum, minimum=minimum)

        if show_progress:
            for _ in tqdm(range(self.max_iterations), mininterval=1):
                self.run_step()
                if self.time_steps % step_size == 0:
                    if stop_condition.check_convergence(self.network):
                        break
        else:
            for _ in range(self.max_iterations):
                self.run_step()
                if self.time_steps % step_size == 0:
                    if stop_condition.check_convergence(self.network):
                        break

    def _run_until_convergence(self, show_progress: bool = False):
        """
        The convergence of the simulation is periodically checked using a custom convergence check 
        set in self.stop_condition. Every step_size steps (defaults to 100), the check_convergence
        method of this custom stop condition is called. The simulation terminates if this method
        returns true or self.max_iterations is reached.

        :param int=100 step_size: determines how often it should be checked for a change in the network.
        :param bool show_progress: bool determines whether to show progress bar
        """
        try:
            step_size = self.parameter_dict["step_size"]
        except KeyError:
            step_size = 100

        if show_progress:
            for _ in tqdm(range(self.max_iterations), mininterval=1):
                self.run_step()
                if self.time_steps % step_size == 0:
                    if self.stop_condition.check_convergence(self.network, **self.parameter_dict):
                        break
        else:
            for _ in range(self.max_iterations):
                self.run_step()
                if self.time_steps % step_size == 0:
                    if self.stop_condition.check_convergence(self.network, **self.parameter_dict):
                        break

    def _run_until_max_iteration(self, show_progress: bool = False):
        """
        :param bool show_progress: bool determines whether to show progress bar
        """
        if show_progress:
            for _ in tqdm(range(self.max_iterations), mininterval=1):
                self.run_step()
        else:
            for _ in range(self.max_iterations):
                self.run_step()
