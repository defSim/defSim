import networkx as nx
from .CreateOutputTable import OutputTableCreator


class ClusterFinder(OutputTableCreator):

    label = "ClusterFinder"

    def __init__(self, cluster_dissimilarity_threshold: float = 0, strict_zones: bool = False):
        super().__init__()
        self.cluster_dissimilarity_threshold = cluster_dissimilarity_threshold
        self.strict_zones = strict_zones    

    def create_output(self, network: nx.Graph, **kwargs):
        """
        Finds the size and number of cultural regions, zones, or clusters present in the graph. Following Axelrod (1997)
        *regions* are defined as a set of connected nodes with an identical attribute profile.
        *Zones* are sets of connected nodes that have some attribute overlap, such that change is still possible.

        :param network: A NetworkX object
        :param float=0 cluster_dissimilarity_threshold: Threshold :math:`\in [0,1]` that defines the maximal allowed
            dissimilarity between two agents for them to be considered to belong to the same cluster. A value of 0
            returns the strict number of regions
        :param strict_zones: If true, cluster_dissimilarity_threshold is neglected and strict zones are returned (only
            the links with dissimilarity != 1 are preserved)
        :returns: A list with sizes of the retrieved clusters
        """

        networkcopy = network.copy()
        if self.strict_zones:
            remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
                      if dissimilarity == 1]
        else:
            remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
                      if dissimilarity > self.cluster_dissimilarity_threshold]
        networkcopy.remove_edges_from(remove)

        try:  # workaround for DiGraphs (nx.connected_components does not work on them)
            return [len(c) for c in sorted(nx.connected_components(networkcopy), key=len, reverse=True)]
        except:
            return [9999999]
        # todo: implement for DiGraph


class AttributeReporter(OutputTableCreator):

    label = "AttributeReporter"

    def __init__(self, feature: str = None):
        super().__init__()
        self.feature = feature
        self.label = feature

    def create_output(self, network: nx.Graph, **kwargs):
        """

        This function will output a single row of a dataframe where the columns are user-given agent-features and column
        values contain a list of all the agents'  values on the given feature.

        :param network: A NetworkX object
        :param feature: The name of the feature to output
        :return: A list of feature values for each agent
        """

        return list(nx.get_node_attributes(network, self.feature).values())


class AverageDistanceReporter(OutputTableCreator):

    label = "AverageDistance"

    def create_output(self, network: nx.Graph, **kwargs):
        """

        Output the average feature distance across all edges. Based on
        calculated distances in the network (so based on whatever
        distance measure was specified in the simulation).

        :param network: A NetworkX object

        :return: Average distance (float)
        """    

        return sum(nx.get_edge_attributes(network, 'dist').values()) / len(network.edges())


class AverageOpinionReporter(OutputTableCreator):

    label = "AverageOpinion"

    def __init__(self, feature: str = 'f01'):
        super().__init__()
        self.feature = feature     

    def create_output(self, network: nx.Graph, **kwargs):
        """

        Output the average opinion on a feature across all agents. 

        :param network: A NetworkX object

        :return: Average opinion (float)
        """    

        return sum(nx.get_node_attributes(network, self.feature).values()) / len(network.nodes())


class DispersionReporter(OutputTableCreator):

    label = "Dispersion"

    def __init__(self, feature: str = 'f01'):
        super().__init__()
        self.feature = feature

    def create_output(self, network: nx.Graph, **kwargs):
        """
        Report the amount of dispersion defined as the average absolute deviation from the mean on a given feature.
        The implementation mirrors that from [Bramson2016]_

        :param network: A NetworkX object
        :return: Dispersion (float)
        """

        attribute_values = nx.get_node_attributes(network, self.feature).values()
        mu_values = sum(attribute_values) / len(attribute_values)
        dispersion = 2 / len(attribute_values) * sum([abs(i - mu_values) for i in attribute_values])

        return dispersion


class SpreadReporter(OutputTableCreator):

    label = "Spread"

    def __init__(self, feature: str = 'f01'):
        super().__init__()
        self.feature = feature

    def create_output(self, network: nx.Graph, **kwargs):
        """
        Report the spread defined as the difference between the maximum and minimum value on a given feature.

        :param network: A NetworkX object
        :return: Spread (float)
        """

        attribute_values = nx.get_node_attributes(network, self.feature).values()

        return (max(attribute_values) - min(attribute_values))


class CoverageReporter(OutputTableCreator):
    label = "Coverage"

    def __init__(self, feature: str = 'f01'):
        super().__init__()
        self.feature = feature

    def create_output(self, network: nx.Graph, **kwargs):
        """
        Report coverage for nondiscrete features, following [Bramson2016]_.
        Its goal is to report the proportion of distinct opinion positions held by the agents in the model.
        To find this proportion, each opinion position receives a bin (or 'halo') around the position of size 1 over
        the number of agents in the network.
        Coverage is then defined as proportion of the total area that is covered by the bins.
        Coverage is maximized if all agents hold unique positions and bins have zero overlap.
        The minimum coverage value is equal to 1 divided by the number of agents in the network.

        :param network: A NetworkX object
        :return: Coverage (float)
        """

        sortdata = sorted(nx.get_node_attributes(network, self.feature).values())

        halo_radius = 0.5 / len(network.nodes)
        lo_bounds = [i - halo_radius for i in sortdata]
        hi_bounds = [i + halo_radius for i in sortdata]

        area_not_covered = 0

        for i in range(len(sortdata)):
            if i == 1:
                if lo_bounds[i] > 0:
                    area_not_covered += lo_bounds[i]
            elif i < (len(sortdata) - 1):
                if lo_bounds[i] > hi_bounds[i - 1]:
                    area_not_covered += lo_bounds[i] - hi_bounds[i - 1]
            else:  # i == len(sortdata)-1
                if hi_bounds[i] < 1:
                    area_not_covered += 1 - hi_bounds[i]
        return (1 - area_not_covered)