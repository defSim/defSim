import networkx as nx
from .agents_init import set_continuous_attribute
from .agents_init import AttributesInitializer


class RandomContinuousInitializer(AttributesInitializer):
    """
    Implements the AttributesInitializer as a random initialization of arbitrary continuous features.

    """
    @staticmethod
    def initialize_attributes(network: nx.Graph, **kwargs):
        """

        Randomly initializes a number of continuous features between 0 and 1 for each node.

        :param network: The graph object whose nodes' attributes are modified.
        :param int=1 num_features: How many different attributes each node has.
        """
        try:
            num_features = kwargs["num_features"]
        except KeyError:
            # print("Number of features was not specified, default value 5 is used.")
            num_features = 1

        for i in range(num_features):
            set_continuous_attribute(network, 'f' + str("%02d" % (i + 1)))