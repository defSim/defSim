import inspect
from abc import ABC, abstractmethod
import networkx as nx
from typing import List

_implemented_output_realizations = ["Basic", "ClusterFinderList", "ClusterFinder", "RegionsList", "Regions",
                                    "ZonesList", "Zones", "Isolates", "AverageDistance", "AverageOpinion",
                                    "Spread", "Dispersion", "Coverage", "Graph"]

class OutputTableCreator(ABC):
    """
    This class is responsible for creating output for the output table.
    Inherit from this class and implement the create_output method to generate the desired output cell for the output table.
    If you want the output cell to have a descriptive column name, overwrite the class variable 'label'. Otherwise, 
    column names are autogenerated.
    """

    label = ""

    def __init__(self, **kwargs):
        pass

    @abstractmethod    
    def create_output(self, network: nx.Graph, **kwargs):
        """
        This method receives a NetworkX object, performs some calculation, and outputs a cell for the output table.

        :param network: A NetworkX graph object.

        :returns: 
        """
        pass


def create_output_table(network: nx.Graph, realizations=None, colnames=None,
                        agents=None, settings_dict=None, tickwise_output=None, **kwargs):
    """
    This function works as a factory method for the OutputTableCreator component.
    It calls the create_output function of a specific implementation of the OutputTableCreator and passes to it
    the kwargs dictionary.

    :param network: A NetworkX object
    :param realizations: The specific OutputTableCreator that will be used. Currently, the options are:

        * Basic: Returns the realizations Regions, Zones, Isolates, Homogeneity, AverageDistance
        * ClusterFinder: Method to find clusters based on minimal allowed distance between network neighbors as
          defined by the user in the kwargs dictionary. Default is to return the same output as the Regions realization
        * Regions: Returns the number of regions (i.e. the number of connected components in the graph after preserving
          only the links with perfect similarity)
        * RegionsList: Returns a list with the sizes of all regions (i.e. the number of agents in each connected
          component in the graph after preserving only the links with perfect similarity)
        * Zones: Returns the number of zones (i.e. the number of connected components in the graph after preserving
          only the links with dissimilarity != 1)
        * ZonesList: Returns a list with the sizes of all zones (i.e. the number of agents in each connected component
          in the graph after preserving only the links with dissimilarity != 1)
        * Isolates: Reports the number of isolates as found in the ClusterFinder method, based on minimal allowed
          distance between network network neighbors as defined by the user in the kwargs dictionary. Default is to
          return the same output as the Regions realization
        * Homogeneity: Size of the largest cluster divided by the number of agents
        * AverageDistance: Reports average distance between connected agents, based on dissimilarity calculated during
          simulation.
        * AverageOpinion: Reports average opinion (requires a list of features for which this needs to be calculated if
          number of features > 1. Pass this list in the kwargs dictionary as AverageOpinionFeatures.)
        * Spread: Reports the spread (distance between maximum and minimum opinion)
        * Dispersion: Returns the amount of dispersion defined as the average absolute deviation from the mean on a
          given feature [Bramson2016]_
        * Coverage: Report coverage for nondiscrete features, following [Bramson2016]_
        * Graph: Returns the entire NetworkX Graph

    :param agents: A list of the indices of all agents that will be considered by the output table.
    :param settings_dict: A dictionary of column names and values that will be added to the output table. Can be used
        to merge output with parameter setting values.
    :param tickwise_output: A dictionary with a list of lists with values of agents on some given feature at each tick
        during the simulation run. This function will create a column for each key in the dictionary.

    :returns: A dictionary.
    """

    # work on a copy of the network, to avoid permanently altering anything
    network = network.copy()

    if colnames is None:
        colnames = []
    if realizations is None:
        realizations = []
    if tickwise_output is None:
        tickwise_output = {}
    if settings_dict is None:
        settings_dict = {}
    if agents is None:
        agents = []

    if len(agents) > 0:
        removenodes = list(set(list(network.nodes())) - set(agents))
        for i in removenodes:
            network.remove_node(i)

    from .OutputMeasures import ClusterFinder, AverageDistanceReporter, AverageOpinionReporter, SpreadReporter, DispersionReporter, CoverageReporter

    # Initialize output dictionary by including settings for the simulation run
    output = settings_dict

    # Create default outputs (called by name)
    ## workaround to call the ClusterFinder method only once
    cluster_dissimilarity_threshold = kwargs.get('cluster_dissimilarity_threshold', 0)
    strict_zones = kwargs.get('strict_zones', False)
    if any([i in realizations for i in ["Clusters", "ClusterList", "Basic", "Isolates", "Homogeneity"]]):
        clusterlist = ClusterFinder(cluster_dissimilarity_threshold=cluster_dissimilarity_threshold, strict_zones=strict_zones).create_output(network, **kwargs)

    # Output related to clustering
    if "ClusterList" in realizations:
        output['ClusterList'] = clusterlist
    if "ClusterFinder" in realizations:
        output['Clusters'] = len(clusterlist)
    if "RegionsList" in realizations:
        output['RegionsList'] = ClusterFinder().create_output(network)
    if any([i in realizations for i in ["Regions", "Basic"]]):
        output['Regions'] = len(ClusterFinder().create_output(network))
    if "ZonesList" in realizations:
        output['ZonesList'] = ClusterFinder(strict_zones=True).create_output(network)
    if any([i in realizations for i in ["Zones", "Basic"]]):
        output['Zones'] = len(ClusterFinder(strict_zones=True).create_output(network))
    if "Isolates" in realizations:
        output['Isolates'] = clusterlist.count(1)
    if any([i in realizations for i in ["Homogeneity", "Basic"]]):
        output['Homogeneity'] = clusterlist[0] / len(network.nodes())

    # Output related to opinions and opinion distances
    if any([i in realizations for i in ["AverageDistance", "Basic"]]):
        output['AverageDistance'] = AverageDistanceReporter().create_output(network)
    if any([i in realizations for i in ["AverageOpinion", "Basic"]]):
        opinionfeatures = kwargs.get("AverageOpinionFeatures", ['f01'])
        for i in opinionfeatures:
            output['AverageOpinion{}'.format(i)] = AverageOpinionReporter(feature = i).create_output(network)
    if "Spread" in realizations:
        opinionfeatures = kwargs.get("SpreadOpinionFeatures", ['f01'])
        for i in opinionfeatures:
            output['Spread{}'.format(i)] = SpreadReporter(feature=i).create_output(network)
    if "Dispersion" in realizations:
        opinionfeatures = kwargs.get("DispersionOpinionFeatures", ['f01'])
        for i in opinionfeatures:
            output['Dispersion{}'.format(i)] = DispersionReporter(feature=i).create_output(network)
    if "Coverage" in realizations:
        opinionfeatures = kwargs.get("CoverageOpinionFeatures", ['f01'])
        for i in opinionfeatures:
            output['Coverage{}'.format(i)] = CoverageReporter(feature=i).create_output(network)

    # Output the entire networkX Graph object
    if "Graph" in realizations:
        output['Graph'] = network

    # Create custom outputs (by calling implementations of OutputTableCreator)
    ## Select only those realizations which are classes (not instances of a class) and of those only if they are a subclass of OutputTableCreator
    custom_realizations = [realization for realization in realizations if (inspect.isclass(realization) and issubclass(realization, OutputTableCreator)) or isinstance(realization, OutputTableCreator)]
    for realization in custom_realizations:
        if realization.label != "":
            output[realization.label] = realization.create_output(network)
        else:
            output["CustomOutput{}".format(custom_realizations.index(realization))] = realization.create_output(network)

    # Add tickwise output if applicable
    if tickwise_output:
        for f in tickwise_output.keys():
            output['Tickwise_' + str(f)] = tickwise_output[f]

    if colnames != []:
        for i in colnames:
            output[i] = output.pop(realizations[colnames.index(i)])

    return output