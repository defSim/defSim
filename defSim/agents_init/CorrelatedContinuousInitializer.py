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
    def initialize_attributes(network: nx.Graph, num_features: int = None, distribution: str = 'uniform', covariances: [list] or np.array = None, correlation: float = None, **kwargs):
        """
        Randomly initializes a number of continuous features between 0 and 1 for each node.
        Specify either a covariance matrix or a single correlation value (which is then applied to all pairs of attributes).
        Correlation values can  be used in the covariance matrix as the base data generated will always be N(0, 1) regardless of the 
        distribution which is eventually returned.
        If both are specified only the covariance matrix is used.
        :param network: The graph object whose nodes' attributes are modified.
        :param int=1 num_features: How many different attributes each node has.
        :param str='uniform' distribution: Type of continuous distribution to draw feature values from.
        :param [list] or numpy.array covariances: Complete covariance matrix (see agents_init.generate_correlated_continuous_attributes)
        :param float correlation: Single correlation value to apply to all pairs of attributes
        """        
        
        if num_features is None:
            warnings.warn("Number of features not specified, using 2 as default")
            num_features = 2
            
        if not distribution in ["uniform", "gaussian"]:
            raise NotImplementedError("The selected distribution has not been implemented. Select from: ['uniform', 'gaussian'].")
        
        if covariances is None:
            if correlation is None:
                warnings.warn("Neither covariance matrix nor correlation specified, using r = 0.5 as default")
                correlation = 0.5
            covariances = []
            for i in range(num_features):
                covariances.append([correlation if not i == j else 1 for j in range(num_features)])
            print(covariances)
            
        if not isinstance(covariances, np.ndarray):
            covariances = np.array(covariances)
        
        n_agents = len(network.nodes)
        features = generate_correlated_continuous_attributes(num_features, n_agents, covariances, distribution)
        print(np.corrcoef(features))
        
        for feature_num, feature in enumerate(features):
            feature_name = 'f' + str("%02d" % (feature_num + 1))
            for node_num, node in enumerate(network.nodes):
                network.nodes[node][feature_name] = feature[node_num]
                      