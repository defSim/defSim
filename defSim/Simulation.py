from typing import List
import random
import time
import pandas as pd
import networkx as nx
import networkx.algorithms.isomorphism as iso
from defSim.network_init import network_init
from defSim.agents_init import agents_init
from defSim.focal_agent_sim import focal_agent_sim
from defSim.neighbor_selector_sim import neighbor_selector_sim
from defSim.influence_sim import influence_sim
from defSim.network_evolution_sim import network_evolution_sim
from defSim.tools import NetworkDistanceUpdater
from defSim.dissimilarity_component.dissimilarity_calculator import DissimilarityCalculator
from defSim.dissimilarity_component.dissimilarity_calculator import select_calculator
from defSim.tools import OutputMeasures


class Simulation:
    """
    This class is responsible for initializing and running a single experiment until the desired stop criterion is
    reached. The Simulation class contains three different stop criterion implementations as methods, but more can be
    added todo: (or passed as a function?).
    The class is initialized in a similar way as the Experiment class but it does not accept multiple parameter
    values per parameter and also all optional parameters are passed in one combined dictionary.

    Args:
        network (nx.Graph=None): A Graph object that was created from empirical data.
        topology (String = "grid"): Options are "grid", "ring" and "spatial_random_graph".
        attributes_initializer (String = "random_categorical" or :class:`AttributesInitializer`): Either be a custom AttributesInitializer or a string that selects from the predefined choices: ["random_categorical", "random_continuous"...]
        focal_agent_selector (str = "random" or :class:`FocalAgentSelector`): Either a custom FocalAgentSelector or a string that selects from the predefined options ["random", ...]
        neighbor_selector (str = "random" or :class:`NeighborSelector`): Either a custom NeighborSelector or a string that selects from the predefined options ["random", ...}
        influence_function (str = "axelrod" or :class:`InfluenceOperator`): Either a custom influence function or a string that selects from the predefined options ["axelrod", "bounded_confidence", "weighted_linear", ...}
        influenceable_attributes (List = None): This is a list of the attribute names, that may be changed in the influence step
        dissimilarity_measure (String = "hamming" or :class:`DissimilarityCalculator`): Either a custom DissimilarityCalculator or a string that selects from the predefined options ["hamming", "euclidean", ...}
        network_modifier: (String = "random" or :class:`NetworkModifier`) Either a custom NetworkModifier or a string selecting from the predefined options ["random", ...]
        stop_condition (str = "max_iteration"): Determines at what point a simulation is supposed to stop. Options include "strict_convergence", which means that it is theoretically not possible anymore for any agent to influence another, "pragmatic_convergence", which means that it is assumed that little change is possible anymore, and "max_iteration" which just stops the simulation after a certain amount of time steps.
        communication_regime (str = "one-to-one"): Options are "one-to-one", "one-to-many" and "many-to-one".
        parameter_dict: A dictionary with all parameters that will be passed to the specific component implementations.
    """

    def __init__(self,
                 network=None,
                 topology: str = "grid",
                 attributes_initializer: str = "random_categorical" or agents_init.AttributesInitializer,
                 focal_agent_selector: str = "random" or focal_agent_sim.FocalAgentSelector,
                 neighbor_selector: str = "random" or neighbor_selector_sim.NeighborSelector,
                 influence_function: str = "axelrod" or influence_sim.InfluenceOperator,
                 influenceable_attributes: List = None,
                 dissimilarity_measure: str = "hamming" or DissimilarityCalculator,
                 network_modifier: str = "random" or network_evolution_sim.NetworkModifier,
                 stop_condition: str = "max_iteration",
                 max_iterations: int = 100000,
                 communication_regime: str = "one-to-one",
                 parameter_dict={},
                 seed=None
                 ):
        self.network = network
        self.topology = topology
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

    def return_values(self):
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


    def run_simulation(self) -> pd.DataFrame:
        """
        This method initializes the network if none is given, initializes the attributes of the agents, and also
        computes and sets the distances between each neighbor.
        It then calls different functions that execute the simulation based on which stop criterion was selected.

        :returns: A pandas Dataframe that contains one row of data. To see what output the output contains see
            :func:`~create_output_table`

        """
        self.initialize_simulation()

        if self.stop_condition == "pragmatic_convergence":
            self._run_until_pragmatic_convergence()
        elif self.stop_condition == "strict_convergence":
            self._run_until_strict_convergence()

        elif self.stop_condition == "max_iteration":
            self._run_until_max_iteration()
        else:
            raise ValueError("Can only select from the options ['Convergence', 'Alternative1', 'Alternative2']")

        return self.create_output_table()

    def initialize_simulation(self):
        """
        This method initializes the network if none is given, initializes the attributes of the agents, and also
        computes and sets the distances between each neighbor.
        """
        if self.seed is None:
            self.seed = random.randint(10000,99999)
        random.seed(self.seed)
        if self.network is None:
            self.network = network_init.generate_network(self.topology, **self.parameter_dict)

        # storing the indices of the agents to access them quicker
        self.agentIDs = list(self.network)

        if isinstance(self.attributes_initializer, agents_init.AttributesInitializer):
            self.attributes_initializer.initialize_attributes(self.network, **self.parameter_dict)
        else:
            agents_init.initialize_attributes(self.network, self.attributes_initializer, **self.parameter_dict)
        # initialization of distances between neighbors
        self.dissimilarity_calculator.calculate_dissimilarity_networkwide(self.network)

    def run_simulation_step(self):
        """
        Executes one iteration of the simulation step which includes the selection of a focal agent, the selection
        of the neighbors and the influence step.
        If the user passed their own implementations of those components, they will be called to execute these steps,
        otherwise the respective factory functions will be called.
        """
        if isinstance(self.focal_agent_selector, focal_agent_sim.FocalAgentSelector):
            selected_agent = self.focal_agent_selector.select_agent(self.network, self.agentIDs, **self.parameter_dict)
        else:
            selected_agent = focal_agent_sim.select_focal_agent(self.network, self.focal_agent_selector,
                                                                self.agentIDs)
        if isinstance(self.neighbor_selector, neighbor_selector_sim.NeighborSelector):
            neighbors = self.neighbor_selector.select_neighbors(self.network, selected_agent,
                                                                   self.communication_regime, **self.parameter_dict)
        else:
            neighbors = neighbor_selector_sim.select_neighbors(self.network, self.neighbor_selector,
                                                                  selected_agent,
                                                                  self.communication_regime, **self.parameter_dict)
        if isinstance(self.influence_function, influence_sim.InfluenceOperator):
            success = self.influence_function.spread_influence(self.network,
                                                               selected_agent,
                                                               neighbors,
                                                               self.communication_regime,
                                                               self.dissimilarity_calculator,
                                                               self.influenceable_attributes,
                                                               **self.parameter_dict)
        else:
            success = influence_sim.spread_influence(self.network,
                                                     self.influence_function,
                                                     selected_agent,
                                                     neighbors,
                                                     self.communication_regime,
                                                     self.dissimilarity_calculator,
                                                     self.influenceable_attributes,
                                                     **self.parameter_dict)
        self.time_steps += 1
        if success:
            self.influence_steps += 1

    def create_output_table(self) -> pd.DataFrame:
        """
        This method measures multiple characteristics of the network in its current state and writes them to a Pandas
        DataFrame. It contains the following columns: \n
        seed: The random seed that was used. \n
        topology: Which network topology was used. \n
        ticks: For how many iterations the simulation ran (so far). \n
        influence_success: How often an agent was successfully influenced by another agent.\n
        clusters: A list containing the sizes of each cluster in descending order.\n
        regions: The total number of regions in the network, i.e. sets of connected nodes with an identical
            attribute profile\n
        zones: The total number of zones in the network, i.e. sets of connected nodes that have some overlap in
            their attribute profile\n
        isolates: The number of nodes in the network that with a strictly dissimilar attribute profile to all of their
            connected nodes\n
        homogeneity: A number between 0 and 1 representing the ratio of the size of the biggest region to the
            number of agents in the network.\n

        :returns: A Pandas DataFrame with one row.
        """
        results = pd.DataFrame({"seed": self.seed}, index=[0])
        if self.network_provided:
            results = results.join(pd.DataFrame({"topology": "pre-loaded"}, index=[0]))
        else:
            results = results.join(pd.DataFrame({"topology": self.topology}, index=[0]))
        results = results.join(pd.DataFrame.from_records(self.parameter_dict, index=[0]))
        results = results.join(pd.DataFrame({"ticks": self.time_steps}, index=[0]))
        results = results.join(pd.DataFrame({"influence_success": self.influence_steps}, index=[0]))
        clusterlist = OutputMeasures.find_clusters(self.network)
        results = results.join(pd.DataFrame({"clusters": str(clusterlist)}, index=[0]))
        results = results.join(pd.DataFrame({"regions": len(clusterlist)}, index=[0]))
        results = results.join(
            pd.DataFrame({"zones": len(OutputMeasures.find_clusters(self.network, strict_zones=True))},
                         index=[0]))
        results = results.join(pd.DataFrame({"isolates": clusterlist.count(1)},
                                            index=[0]))
        results = results.join(pd.DataFrame({"homogeneity":
            OutputMeasures.find_clusters(self.network)[0] / len(self.network.nodes())}, index=[0]))

        return results

    def _run_until_pragmatic_convergence(self):
        """
        Pragmatic convergence means that each "step_size" time steps it is checked whether the structure of the network
        and all attributes are still the same. If thats the case, it is assumed that the simulation converged and it stops.

        :param int=100 step_size: determines how often it should be checked for a change in the network.
        """
        try:
            step_size = self.parameter_dict["step_size"]
        except KeyError:
            step_size = 100

        all_attributes = self.network.node[1].keys()
        node_matcher = iso.categorical_node_match(all_attributes, [0 for i in range(len(all_attributes))])
        network_comparison = self.network.copy()
        while 1:
            self.run_simulation_step()
            if self.time_steps == self.max_iterations:
                break
            if self.time_steps % step_size == 0:
                if nx.is_isomorphic(self.network, network_comparison, node_match=node_matcher):
                    break
                else:
                    network_comparison = self.network.copy()

    def _run_until_strict_convergence(self):
        """
        Here the convergence of the simulation is periodically checked by assessing the distance between each neighbor
        in the network. Unless there is no single pair left that can theoretically influence each other, the simulation
        continues.

        :param float=0.0 threshold: A value between 0 and 1 that determines at what distance two agents can't influence each other anymore.
        :param boolean=True check_each_step: A boolean that determines whether convergence should be checked each step or only every hundreth
            step to save time.
        """
        try:
            threshold = self.parameter_dict["threshold"]
        except KeyError:
            threshold = 0.0
        try:
            check_each_step = self.parameter_dict["check_each_step"]
        except KeyError:
            check_each_step = True

        self.time_steps = 0
        if check_each_step:
            while 1:
                self.run_simulation_step()
                if self.time_steps == self.max_iterations:
                    break
                if not NetworkDistanceUpdater.check_dissimilarity(self.network, threshold):
                    break
        else:
            while 1:
                self.run_simulation_step()
                if self.time_steps == self.max_iterations:
                    break
                if self.time_steps % 100 == 0:
                    if not NetworkDistanceUpdater.check_dissimilarity(self.network, threshold):
                        break

    def _run_until_max_iteration(self):
        for iteration in range(self.max_iterations):
            self.run_simulation_step()
