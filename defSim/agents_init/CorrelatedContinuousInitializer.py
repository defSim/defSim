import networkx as nx
import numpy as np
import warnings
from .agents_init import AttributesInitializer
from .agents_init import generate_correlated_continuous_attributes


class CorrelatedContinuousInitializer(AttributesInitializer):    
    """
    Implements the AttributesInitializer as a random initialization of correlated random continuous features.
    """
    
    @staticmethod
    def initialize_attributes(network: nx.Graph, distribution: str = 'uniform', **kwargs):
        """
        Randomly initializes a number of continuous features between 0 and 1 for each node.
        Specify either a covariance matrix or a single correlation value (which is then applied to all pairs of attributes).
        Correlation values can  be used in the covariance matrix as the base data generated will always be N(0, 1) regardless of the 
        distribution which is eventually returned.
        If both are specified only the covariance matrix is used.
        :param network: The graph object whose nodes' attributes are modified.
        :param str='uniform' distribution: Type of continuous distribution to draw feature values from.
        :param int=1 num_features: How many different attributes each node has.        
        :param [list] or numpy.array covariances: Complete covariance matrix (see agents_init.generate_correlated_continuous_attributes)
        :param float correlation: Single correlation value to apply to all pairs of attributes
        """        

        if not distribution in ["uniform", "gaussian"]:
            raise NotImplementedError("The selected distribution has not been implemented. Select from: ['uniform', 'gaussian'].")               

        try:
            num_features = kwargs["num_features"]
        except KeyError:
            warnings.warn("Number of features not specified, using 2 as default")
            num_features = 2
    
        covariances = kwargs.get("covariances", None)
        correlation = kwargs.get("correlation", None)
        
        if covariances is None:
            if correlation is None:
                warnings.warn("Neither covariance matrix nor correlation specified, using r = 0.5 as default")
                correlation = 0.5
            covariances = []
            for i in range(num_features):
                covariances.append([correlation if not i == j else 1 for j in range(num_features)])
        
        n_agents = len(network.nodes)
        feature_values = generate_correlated_continuous_attributes(num_features, n_agents, covariances, distribution)
        
        feature_names = ['f' + str("%02d" % (feature_num + 1)) for feature_num in range(num_features)]
        for node_num, node in enumerate(network.nodes):
            for feature_num, feature in enumerate(feature_names):
                network.nodes[node][feature] = feature_values[node_num, feature_num]
                      