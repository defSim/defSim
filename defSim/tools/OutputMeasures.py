import networkx as nx
from .CreateOutputTable import OutputTableCreator


class ClusterFinder(OutputTableCreator):
    @staticmethod
    def create_output(network: nx.Graph, **kwargs):
        """
        Finds the size and number of cultural regions, zones, or clusters present in the graph. Following Axelrod (1997)
        *regions* are defined as a set of connected nodes with an identical attribute profile.
        *Zones* are sets of connected nodes that have some attribute overlap, such that change is still possible.

        :param network: A NetworkX object
        :param float=0 cluster_dissimilarity_threshold: Threshold :math:`\in [0,1]` that defines the maximal allowed
        dissimilarity between two agents for them to be considered to belong to the same cluster. A value of 0 returns the
        strict number of regions
        :param strict_zones: If true, cluster_dissimilarity_threshold is neglected and strict zones are returned (only the
        links with dissimilarity != 1 are preserved)
        :returns: A list with sizes of the retrieved clusters
        """
        cluster_dissimilarity_threshold = kwargs.get('cluster_dissimilarity_threshold', 0)
        strict_zones = kwargs.get('strict_zones', False)

        networkcopy = network.copy()
        if strict_zones:
            remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
                      if dissimilarity == 1]
        else:
            remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
                      if dissimilarity > cluster_dissimilarity_threshold]
        networkcopy.remove_edges_from(remove)

        return [len(c) for c in sorted(nx.connected_components(networkcopy), key=len, reverse=True)]

class AttributeReporter(OutputTableCreator):
    @staticmethod
    def create_output(network: nx.Graph, **kwargs):
        """

        THIS FUNCTION WILL OUTPUT A SINGLE ROW OF A DATAFRAME WHERE THE COLUMNS ARE USER-GIVEN AGENT-FEATURES AND COLUMN
        VALUES CONTAIN A LIST OF ALL THE AGENTS' VALUES ON THE GIVEN FEATURE.

        :param network:
        :param feature:
        :return:
        """

        feature = kwargs.get('feature', False)

        return list(nx.get_node_attributes(network, feature).values())
