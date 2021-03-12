import networkx as nx
from .agents_init import set_categorical_attribute
from .agents_init import AttributesInitializer


class RandomCategoricalInitializer(AttributesInitializer):
    """
    Implements the AttributesInitializer as a random initialization of arbitrary discrete features.
    """

    def __init__(self, **kwargs):
        """
        :param int=5 num_features: How many different attributes each node has.
        :param int=3 num_traits: The range of values each attribute can take. 3 means that an attribute can be either 0, 1 or 2
        """

        try:
            self.num_features = kwargs["num_features"]
        except KeyError:
            #print("Number of features was not specified, default value 5 is used.")
            self.num_features = 5
        try:
            self.num_traits = kwargs["num_traits"]
        except KeyError:
            #print("Number of traits was not specified, default value 3 is used.")
            self.num_traits = 3        

    def initialize_attributes(self, network: nx.Graph, **kwargs):
        """
        Randomly initializes a number of discrete features for each node.

        :param network: The graph object whose nodes' attributes are modified.
        """

        for i in range(self.num_features):
            set_categorical_attribute(network, 'f' + str("%02d" % (i + 1)), [i for i in range(self.num_traits)])





