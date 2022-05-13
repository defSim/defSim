from unittest import TestCase
import defSim as ds

class test_find_clusters(TestCase):
    # initialize network and attributes
    G = ds.generate_network('complete_graph', n=4)
    ds.agents_init.initialize_attributes(G, 'random_categorical', num_features=3, num_traits=2)
    # change attribute values
    G.nodes[0].update(dict(zip(['f01', 'f02', 'f03'], (1, 1, 1))))
    G.nodes[1].update(dict(zip(['f01', 'f02', 'f03'], (1, 1, 1))))
    G.nodes[2].update(dict(zip(['f01', 'f02', 'f03'], (1, 0, 0))))
    G.nodes[3].update(dict(zip(['f01', 'f02', 'f03'], (0, 0, 0))))
    # update dissimilarity in the network
    calculator = ds.dissimilarity_calculator.select_calculator('hamming')
    calculator.calculate_dissimilarity_networkwide(G)

    # the list of sizes of clusters of unique attribute profiles:
    assert ds.OutputMeasures.ClusterFinder().create_output(G) == [2, 1, 1]
    # the list of sizes of clusters in which influence is still possible:
    assert ds.OutputMeasures.ClusterFinder(strict_zones=True).create_output(G) == [4]
    # the list of sizes of clusters with reasonably similar attribute profiles
    assert ds.OutputMeasures.ClusterFinder(cluster_dissimilarity_threshold=.5).create_output(G) == [2, 2]