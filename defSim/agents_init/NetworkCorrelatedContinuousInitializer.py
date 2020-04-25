import networkx as nx
import numpy as np
import scipy.stats as stats
import warnings
import random
from .agents_init import AttributesInitializer
from .agents_init import generate_correlated_continuous_attributes


class NetworkCorrelatedContinuousInitializer(AttributesInitializer):    
    """
    Implements the AttributesInitializer as a random initialization of correlated random continuous features,
    with the added property of correlating feature value with network position.
    """
    
    @staticmethod
    def initialize_attributes(network: nx.Graph, distribution: str = 'uniform', **kwargs):
        """
        Randomly initializes a number of continuous features between 0 and 1 for each node.
        Specify either a covariance matrix or a single correlation value (which is then applied to all pairs of attributes).
        Correlation values can  be used in the covariance matrix as the base data generated will always be N(0, 1) regardless of the 
        distribution which is eventually returned.
        If both are specified only the covariance matrix is used.
        
        The generated feature values are then spread across the network in a non-random way, by placing more weight on attribute values
        close to the current mean value of the first attribute among network neighbors. Weights are bsaed on a Beta distribution with
        its mode set to the mean value among neighbors. The concentration of weights around the mode can be adjusted with the 
        'neighbor_influence_concentration' parameter. The strength of neighbor influence can be adjusted using the 'neighbor_influence_strength' parameter. 
        
        :param network: The graph object whose nodes' attributes are modified.
        :param str='uniform' distribution: Type of continuous distribution to draw feature values from.
        :param float=10 neighbor_influence_concentration: How closely concentrated (peaked) the weight distribution is around the mean value of neighbors (minimum value > 2 required to maintain integrity of the distribution)
        :param float=1 neighbor_influence_strength: Strength of weighting by neighbor value. 0 = no influence of neighbors
        :param int=1 num_features: How many different attributes each node has.  
        :param str='f01' neighbor_influence_feature: Sets the feature on which neighbor similarity will be determined.
        :param [list] or numpy.array covariances: Complete covariance matrix (see agents_init.generate_correlated_continuous_attributes)
        :param float correlation: Single correlation value to apply to all pairs of attributes
        :param bool allow_inverse_concentration: Use to allow concentrations below 2, which result in anticoordination with neighbors
        """   
        
        # Check inputs
        if not distribution in ["uniform", "gaussian"]:
            raise NotImplementedError("The selected distribution has not been implemented. Select from: ['uniform', 'gaussian'].")               

        try:
            num_features = kwargs["num_features"]
        except KeyError:
            warnings.warn("Number of features not specified, using 1 as default")
            num_features = 1
            
        neighbor_influence_concentration = kwargs.get("neighbor_influence_concentration", 10)
        allow_inverse_concentration = kwargs.get("allow_inverse_concentration", False)
        if neighbor_influence_concentration <= 2 and not allow_inverse_concentration:
            raise ValueError("neighbor_influence_concentration must be greater than 2 to maintain single-peaked distribution. Set 'allow_inverse_concentration' to True to override.")
        elif neighbor_influence_concentration <= 0:
            raise ValueError("neighbor_influence_concentration must be greater than  0.")
            
        neighbor_influence_strength = kwargs.get("neighbor_influence_strength", 10)
        if neighbor_influence_strength < 0:
            raise ValueError("neighbor_influence_strength cannot be negative (to avoid negative choice weights). Try 0 < neighbor_influence_concentration < 2 instead for anticoordinatoin with neighbors.")
    
        neighbor_influence_feature = kwargs.get("neighbor_influence_feature", "f01")

        covariances = kwargs.get("covariances", None)
        correlation = kwargs.get("correlation", None)


        # Generate feature values
        if covariances is None:
            if correlation is None:
                correlation = 0
                if num_features > 0:
                    warnings.warn("Neither covariance matrix nor correlation specified, using r = 0 as default")
            covariances = []
            for i in range(num_features):
                covariances.append([correlation if not i == j else 1 for j in range(num_features)])
            
        if not isinstance(covariances, np.ndarray):
            covariances = np.array(covariances)
        
        n_agents = len(network.nodes)
        feature_values = generate_correlated_continuous_attributes(num_features, n_agents, covariances, distribution)
        
        
        # Distribute features across network
        ## sort features by first column (first feature)
        sorted_indexes = np.argsort(feature_values[:,0] )
        sorted_features = feature_values[sorted_indexes]
        
        ## the code beyond this point only works with values ranging between 0 and 1
        if (np.amin(sorted_features) < 0) or (np.amax(sorted_features) > 1):
            raise ValueError('Attribute values outside range [0,1] not supported. Rescale first.')
        
        ## get a list of all nodes, in random order
        nodes_list = list(network.nodes)
        random.shuffle(nodes_list)
        
        ## first initialize all features for all nodes 
        feature_names = ['f' + str("%02d" % (feature_num + 1)) for feature_num in range(num_features)]
        for node in network.nodes:
            for feature in feature_names:
                network.nodes[node][feature] = None
        
        # assign attribute values with weights determined by average value of network neighbors
        # on the specified feature
        for node in network.nodes:
            ## initially, all available feature values are equally likely
            weights = [1 for _ in range(np.ma.size(sorted_features, axis = 0))]
            ## collect all 
            neighbor_values = [network.nodes[neighbor][neighbor_influence_feature] for neighbor in network.neighbors(node) if network.nodes[neighbor][neighbor_influence_feature] is not None]
            if len(neighbor_values) > 0:
                mean_neighbor_value = sum(neighbor_values) / len(neighbor_values)
                # set alpha and beta for a beta distribution so that the
                # mode of the distribution is at mean neighbor value
                # peakedness of the distribution is set by 'neighbor_influence_concentration'
                bdist_alpha = mean_neighbor_value*(neighbor_influence_concentration-2)+1
                bdist_beta = (1-mean_neighbor_value)*(neighbor_influence_concentration-2)+1
                # add weight based on beta pdf, scaled by 'neighbor_influence_strength'
                weights = [weight + (neighbor_influence_strength * stats.beta.pdf(sorted_features[index,0], bdist_alpha, bdist_beta)) for index, weight in enumerate(weights)]

            selected_row = random.choices(population = list(range(np.ma.size(sorted_features, axis = 0))), weights = weights, k = 1)
            feature_values = sorted_features[selected_row].tolist()[0]
            sorted_features = np.delete(sorted_features, selected_row, axis = 0)

            for feature_num, feature_name in enumerate(feature_names):
                network.nodes[node][feature_name] = feature_values[feature_num]