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


def clustercount(network):  # returns
    """
    Counts how many clusters exist in the network. #todo: reference on what a cluster is

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


def regionscount(network):  # returns a list with the size of all the clusters in the graph
    """
    Counts how many agents belong to each cluster in the network and returns a list of these numbers.

    :param network: The network to be measured.
    :returns: A list with the size of all the clusters in the graph.
    """
    Gsub = network.copy()
    remove = [pair for pair, dissimilarity in nx.get_edge_attributes(Gsub, 'dist').items() if dissimilarity != 0]
    Gsub.remove_edges_from(remove)
    # changed the return for single run analysis!!!!
    # return([len(c) for c in sorted(nx.connected_components(Gsub), key=len, reverse=True)])
    return (len([len(c) for c in sorted(nx.connected_components(Gsub), key=len, reverse=True)]))
