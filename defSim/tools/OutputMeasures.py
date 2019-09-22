import networkx as nx


# todo: potentially rename clustercount and regionscount (maybe also isol) and add docstring
def homogeneity(network):  # returns
    """
    A measure of how much consensus exists in the network.

    :param network: A NetworkX object
    :returns: The homogeneity measure 'S_max / N'
    """
    Gsub = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(Gsub, 'dist').items() if dissimilarity != 0]
    Gsub.remove_edges_from(remove)
    return (len(sorted(nx.connected_components(Gsub), key=len, reverse=True)[0]) / nx.number_of_nodes(Gsub))


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


def zonescount(network, zones_threshold: float = 1):  # returns
    """
    Counts the number of *cultural zones* present in the graph. Following Axelrod (1997), cultural zones are
    defined as a set of connected nodes with an some remaining overlap. In the model for the dissemination of culture,
    that uses homophily to dictate interaction probabilities, this means that interaction is still possible within the
    cultural zone.

    :param network: A NetworkX object
    :param float=1 zones_threshold: Threshold :math:`\in [0,1]` that defines the maximal allowed dissimilarity between
    two agents to belong to the same zone.
    :returns: The number of zones in the network.
    """
    networkcopy = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
              if dissimilarity < zones_threshold]
    networkcopy.remove_edges_from(remove)

    return len([len(c) for c in sorted(nx.connected_components(networkcopy), key=len, reverse=True)])


def regionscount(network, regions_threshold: float = 0):
    """
    Counts the number of *cultural regions* present in the graph. Following Axelrod (1997), cultural regions are
    defined as a set of connected nodes with an identical cultural profile.

    :param network: A NetworkX object
    :param float=0 regions_threshold: Threshold :math:`\in [0,1]` that defines the maximal allowed dissimilarity between
    two agents to belong to the same region.
    """
    networkcopy = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
              if dissimilarity > regions_threshold]
    networkcopy.remove_edges_from(remove)

    return len([len(c) for c in sorted(nx.connected_components(networkcopy), key=len, reverse=True)])


def clustercount(network, cluster_threshold: float = 1):
    """
    This method returns a list with the size of the cultural clusters within the graph. Whether adjacent nodes belong to
    the same cluster is defined by a threshold that determines the maximal allowed dissimilarity

    :param network: A NetworkX object
    :param float=1 cluster_threshold:
    :returns: A list with the size of all the clusters in the graph.
    """
    networkcopy = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
              if dissimilarity < cluster_threshold]
    networkcopy.remove_edges_from(remove)

    return [len(c) for c in sorted(nx.connected_components(networkcopy), key=len, reverse=True)]

