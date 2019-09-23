import networkx as nx


def isol(network):
    """
    Counts how many agents belong to no cluster.

    :param network: A NetworkX object
    :returns: The count of isolates in the graph.
    """
    Gsub = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(Gsub, 'dist').items() if dissimilarity != 0]
    Gsub.remove_edges_from(remove)
    return len(list(nx.isolates(Gsub)))


def find_clusters(network, cluster_dissimilarity_threshold: float = 0, strict_zones: bool = False):
    """
    Finds the size and number of cultural regions, zones, or clusters present in the graph. Following Axelrod (1997),
    *regions* are defined as a set of connected nodes with an identical attribute profile.
    *Zones* are sets of connected nodes that have some attribute overlap, such that change is still possible.

    :param network: A NetworkX object
    :param float=0 cluster_dissimilarity_threshold: Threshold :math:`\in [0,1]` that defines the maximal allowed
    dissimilarity between two agents for them to be considered to belong to the same cluster. A value of 0 returns the
    strict number of regions
    :param strict_zones: If true, cluster_dissimilarity_threshold is neglected and strict zones are returned (only the
    links with dissimilarity != 1 are preserved
    :returns A list with sizes of the retrieved clusters
    """
    networkcopy = network.copy()
    if strict_zones:
        remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
                  if dissimilarity != 1]
    else:
        remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
                  if dissimilarity > cluster_dissimilarity_threshold]
    networkcopy.remove_edges_from(remove)

    return [len(c) for c in sorted(nx.connected_components(networkcopy), key=len, reverse=True)]