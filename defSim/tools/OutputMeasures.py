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
