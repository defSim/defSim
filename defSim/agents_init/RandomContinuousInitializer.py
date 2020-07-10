import warnings
import networkx as nx
from .agents_init import set_continuous_attribute
from .agents_init import AttributesInitializer


class RandomContinuousInitializer(AttributesInitializer):
    """
    Implements the AttributesInitializer as a random initialization of arbitrary continuous features.

    """

    @staticmethod
    def initialize_attributes(network: nx.Graph, distribution: str = 'uniform', **kwargs):
        """

        Randomly initializes a number of continuous features between 0 and 1 for each node.
        Bounds default to min = 0, max = 1

        :param network: The graph object whose nodes' attributes are modified.
        :param dict={'min': 0, 'max': 1} feature_bounds: Dictionary containing minimum and maximum feature values.
        :param str='uniform' distribution: Type of continuous distribution to draw feature values from.
        :param int=1 num_features: How many different attributes each node has.
        """
        try:
            num_features = kwargs["num_features"]
        except KeyError:
            warnings.warn("Number of features not specified, using 1 as default")
            num_features = 1         

        for i in range(num_features):
            set_continuous_attribute(network, 'f' + str("%02d" % (i + 1)), distribution = distribution)