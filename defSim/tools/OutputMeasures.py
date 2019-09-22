import networkx as nx


# todo: potentially rename clustercount and regionscount (maybe also isol) and add docstring
def homogeneity(network):  # returns
    """
    A measure of how much consensus exists in the network.

    :param network: The network to be measured.
    :returns: The homogeneity measure 'S_max / N'
    """
    Gsub = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(Gsub, 'dist').items() if dissimilarity != 0]
    Gsub.remove_edges_from(remove)
    return (len(sorted(nx.connected_components(Gsub), key=len, reverse=True)[0]) / nx.number_of_nodes(Gsub))


def isol(network):
    """
    Counts how many agents belong to no cluster.

    :param network: The network to be measured.
    :returns: The count of isolates in the graph.
    """
    Gsub = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(Gsub, 'dist').items() if dissimilarity != 0]
    Gsub.remove_edges_from(remove)
    return len(list(nx.isolates(Gsub)))


def zonescount(network):  # returns
    """
    Counts the number of *cultural clusters* present in the graph. Following Axelrod (1997), cultural clusters are
    defined as a set of connected nodes with an some remaining overlap. In the model for the dissemination of culture,
    that uses homophily to dictate interaction probabilities, this means that interaction is still possible within the
    cultural zone.

    :param network: The network to be measured.
    :returns: The number of clusters in the network.
    """
    Gsub = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(Gsub, 'dist').items() if dissimilarity != 0]
    Gsub.remove_edges_from(remove)
    # todo: ask marijn what this means exactly
    # changed the return for single run analysis!!!!
    return ([len(c) for c in sorted(nx.connected_components(Gsub), key=len, reverse=True)])
    # return(len([len(c) for c in sorted(nx.connected_components(Gsub), key=len, reverse=True)]))


def regionscount(network, regions_threshold: float = 0):
    """
    Counts the number of *cultural regions* present in the graph. Following Axelrod (1997), cultural regions are
    defined as a set of connected nodes with an identical cultural profile.

    :param network: The network to be measured.
    :param float=0 regions_threshold: Threshold :math:`\in [0,1]` that defines the maximal allowed dissimilarity between
    two agents to belong to the same region.
    :returns: A list with the size of all the clusters in the graph.
    """
    networkcopy = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(networkcopy, 'dist').items()
              if dissimilarity > regions_threshold]
    networkcopy.remove_edges_from(remove)

    return len([len(c) for c in sorted(nx.connected_components(networkcopy), key=len, reverse=True)])
