import warnings
import networkx as nx
from .agents_init import set_continuous_attribute
from .agents_init import AttributesInitializer


class RandomContinuousInitializer(AttributesInitializer):
    """
    Implements the AttributesInitializer as a random initialization of arbitrary continuous features.

    """

    def __init__(self, distribution: str = 'uniform', **kwargs):
        """
        :param str='uniform' distribution: Type of continuous distribution to draw feature values from.
        :param int=1 num_features: How many different attributes each node has.
        """

        if not distribution in ["uniform", "normal", "beta", "triangular"]:
            raise NotImplementedError("The selected distribution has not been implemented. Select from: [uniform, normal, beta, triangular].")
        self.distribution = distribution

        try:
            self.num_features = kwargs["num_features"]
        except KeyError:
            warnings.warn("Number of features not specified, using 1 as default")
            self.num_features = 1     


    def initialize_attributes(self, network: nx.Graph, **kwargs):
        """

        Randomly initializes a number of continuous features between 0 and 1 for each node.
        Bounds default to min = 0, max = 1

        :param network: The graph object whose nodes' attributes are modified.
        """    

        for i in range(self.num_features):
            set_continuous_attribute(network, 'f' + str("%02d" % (i + 1)), distribution = self.distribution)