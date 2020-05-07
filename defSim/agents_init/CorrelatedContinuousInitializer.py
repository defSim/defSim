import networkx as nx
import numpy as np
import scipy.stats as stats
import math
import warnings
import random
from .agents_init import AttributesInitializer
from .agents_init import generate_correlated_continuous_attributes

def apply_neighbor_similarity_beta_weights(network, feature_values, feature_names, neighbor_similarity_feature, neighbor_similarity_concentration, neighbor_similarity_strength):
    ### TODO: allow select similarity feature ###

    ## first initialize all features for all nodes
    for node in network.nodes:
        for feature in feature_names:
            network.nodes[node][feature] = None        

    ## sort features by first column (first feature)
    sorted_indexes = np.argsort(feature_values[:,0] )
    sorted_features = feature_values[sorted_indexes]
    
    ## the code beyond this point only works with values ranging between 0 and 1
    if (np.amin(sorted_features) < 0) or (np.amax(sorted_features) > 1):
        raise ValueError('Attribute values outside range [0,1] not supported. Rescale first.')
    
    ## get a list of all nodes, in random order
    nodes_list = list(network.nodes)
    random.shuffle(nodes_list)
    
    # assign attribute values with weights determined by average value of network neighbors
    # on the specified feature
    nodes = list(network.nodes)

    for node in nodes:
        ## initially, all available feature values are equally likely
        weights = [1 for _ in range(np.ma.size(sorted_features, axis = 0))]
        ## collect all 
        neighbor_values = [network.nodes[neighbor][neighbor_similarity_feature] for neighbor in network.neighbors(node) if network.nodes[neighbor][neighbor_similarity_feature] is not None]
        if len(neighbor_values) > 0:
            mean_neighbor_value = sum(neighbor_values) / len(neighbor_values)
            # set alpha and beta for a beta distribution so that the
            # mode of the distribution is at mean neighbor value
            # peakedness of the distribution is set by 'neighbor_similarity_concentration'
            bdist_alpha = mean_neighbor_value*(neighbor_similarity_concentration-2)+1
            bdist_beta = (1-mean_neighbor_value)*(neighbor_similarity_concentration-2)+1
            # add weight based on beta pdf, scaled by 'neighbor_similarity_strength'
            weights = [weight + (neighbor_similarity_strength * stats.beta.pdf(sorted_features[index,0], bdist_alpha, bdist_beta)) for index, weight in enumerate(weights)]

        selected_row = random.choices(population = list(range(np.ma.size(sorted_features, axis = 0))), weights = weights, k = 1)
        feature_values = sorted_features[selected_row].tolist()[0]
        sorted_features = np.delete(sorted_features, selected_row, axis = 0)

        for feature_num, feature_name in enumerate(feature_names):
            network.nodes[node][feature_name] = feature_values[feature_num]


class SimilarityPostprocessor():
    def __init__(self, network, dissimilarity_criterion, feature_names, neighbor_similarity_feature):
        self.network = network
        self.dissimilarity_criterion = dissimilarity_criterion
        self.feature_names = feature_names
        self.neighbor_similarity_feature = neighbor_similarity_feature
        self.set_constant_count = 0
        self.constant_num_dissimilar_count = 0


    def dissimilarity_data_for_node(self, node):
        neighbor_values = [self.network.nodes[neighbor][self.neighbor_similarity_feature] for neighbor in self.network.neighbors(node)]
        node_value = self.network.nodes[node][self.neighbor_similarity_feature]
        max_dissimilarity = max([abs(neighbor_val - node_value) for neighbor_val in neighbor_values])

        return [node, max_dissimilarity, node_value]

    def create_dissimilarity_data(self):
        nodes = list(self.network.nodes)

        # go through list once
        dissimilarity_data = []
        for node in nodes:
            dissimilarity_data.append(self.dissimilarity_data_for_node(node))

        self.dissimilarity_data = np.array(dissimilarity_data)                 

    def update_dissimilarity(self, node1, node2):
        node1_neighbors = self.network.neighbors(node1)
        node2_neighbors = self.network.neighbors(node2)

        self.dissimilarity_data[np.where(self.dissimilarity_data[:,0] == node1)] = self.dissimilarity_data_for_node(node1)
        self.dissimilarity_data[np.where(self.dissimilarity_data[:,0] == node2)] = self.dissimilarity_data_for_node(node2)                

        for neighbor in node1_neighbors:
             self.dissimilarity_data[np.where(self.dissimilarity_data[:,0] == neighbor)] = self.dissimilarity_data_for_node(neighbor)

        for neighbor in node2_neighbors:
             self.dissimilarity_data[np.where(self.dissimilarity_data[:,0] == neighbor)] = self.dissimilarity_data_for_node(neighbor)          

    def improvement_if_swapped(self, node1_data, node2_data):
        current_dissimilarity_node1 = node1_data[1]
        current_dissimilarity_node2 = node2_data[1]

        value_node1 = node1_data[2] 
        value_node2 = node2_data[2]

        neighbor_values_node1 = [self.network.nodes[neighbor][self.neighbor_similarity_feature] for neighbor in self.network.neighbors(node1_data[0])]
        neighbor_values_node2 = [self.network.nodes[neighbor][self.neighbor_similarity_feature] for neighbor in self.network.neighbors(node2_data[0])]

        new_dissimilarity_node1 = max([abs(neighbor_val - value_node1) for neighbor_val in neighbor_values_node2])
        new_dissimilarity_node2 = max([abs(neighbor_val - value_node2) for neighbor_val in neighbor_values_node1])

        return (current_dissimilarity_node1**2 + current_dissimilarity_node2**2) - (new_dissimilarity_node1**2 + new_dissimilarity_node2**2)

    def swap_nodes(self, node1, node2):
        for feature_name in self.feature_names:
            node1_old_value = self.network.nodes[node1][feature_name]
            node2_old_value = self.network.nodes[node2][feature_name]
            self.network.nodes[node1][feature_name] = node2_old_value
            self.network.nodes[node2][feature_name] = node1_old_value             
 
    def swap_dissimilar_nodes(self):
        swaps = 0

        # improve most dissimilar  
        too_dissimilar_nodes =  self.dissimilarity_data[np.where(self.dissimilarity_data[:,1] > self.dissimilarity_criterion)]
        for dissimilar_node in too_dissimilar_nodes:
            potential_improvement = np.array([self.improvement_if_swapped(dissimilar_node, other_node) for other_node in self.dissimilarity_data])
            
            if potential_improvement.max() > 0:
                max_improvement_indices = np.argmax(potential_improvement)
                try:
                    other_node = self.dissimilarity_data[max_improvement_indices]
                except TypeError:
                    other_node = self.dissimilarity_data[max_improvement_indices[0]]

                #print("Swapping node {} and {}".format(dissimilar_node[0], other_node[0]))
                self.swap_nodes(dissimilar_node[0], other_node[0])
                self.update_dissimilarity(dissimilar_node[0], other_node[0])
                swaps += 1

        return (swaps, too_dissimilar_nodes)

    def check_convergence(self, swaps, current_dissimilar_nodes, nodes_involved_previous, num_dissimilar_previous):

        if swaps == 0:
            if len(current_dissimilar_nodes) > 0:
                warnings.warn("Set of agents who are too dissimilar is not empty but no improvement is possible. Stopping postprocessing.")
            return True

        set_difference_length = len(set(current_dissimilar_nodes[:,0].tolist()) ^ set(nodes_involved_previous))                  
        if set_difference_length == 0:
            self.set_constant_count += 1
            if self.set_constant_count == 10:
                warnings.warn("Set of agents who are too dissimilar has not changed for {} iterations. Stopping postprocessing.".format(set_constant))
                return True
        else:
            self.set_constant = 0

        if len(current_dissimilar_nodes) == num_dissimilar_previous:
            self.constant_num_dissimilar_count += 1
            if self.constant_num_dissimilar_count == 50:
                warnings.warn("Number of agents too dissimilar has not improved for {} iterations. Stopping postprocessing.".format(constant_num_dissimilar_count))
                return True
        else:
            self.set_constant = 0

        return False

    def process(self, postprocessing_iterations): 

        iteration = 0
        num_dissimilar_previous = 0
        nodes_involved_previous = []
        self.set_constant_count = 0
        self.constant_num_dissimilar_count = 0

        if postprocessing_iterations == "convergence":

            while True:
                iteration += 1       

                swaps, current_dissimilar_nodes = self.swap_dissimilar_nodes()

                if self.check_convergence(swaps, current_dissimilar_nodes, nodes_involved_previous, num_dissimilar_previous):
                    break
                
                nodes_involved_previous = current_dissimilar_nodes[0].tolist()
                num_dissimilar_previous = len(current_dissimilar_nodes) 


        elif postprocessing_iterations > 0:
            for iteration in range(postprocessing_iterations):             

                swaps, current_dissimilar_nodes = self.swap_dissimilar_nodes()

                if self.check_convergence(swaps, current_dissimilar_nodes, nodes_involved_previous, num_dissimilar_previous):
                    break
                
                nodes_involved_previous = current_dissimilar_nodes[0].tolist()
                num_dissimilar_previous = len(current_dissimilar_nodes)                     


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
        
        The generated feature values can be spread across the network in a non-random way, by placing more weight on attribute values
        close to the current mean value of the first attribute among network neighbors. Weights are bsaed on a Beta distribution with
        its mode set to the mean value among neighbors. The concentration of weights around the mode can be adjusted with the 
        'neighbor_similarity_concentration' parameter. The strength of neighbor influence can be adjusted using the 'neighbor_similarity_strength' parameter. 
        When 'neighbor_similarity_strength' == 0 (default) attribute values are randomly assigned to agents.
        
        :param network: The graph object whose nodes' attributes are modified.
        :param str='uniform' distribution: Type of continuous distribution to draw feature values from.
        :param float=10 neighbor_similarity_concentration: How closely concentrated (peaked) the weight distribution is around the mean value of neighbors (minimum value > 2 required to maintain integrity of the distribution)
        :param float=0 neighbor_similarity_strength: Strength of weighting by neighbor value. 0 = no influence of neighbors
        :param int=1 num_features: How many different attributes each node has.  
        :param str='f01' neighbor_similarity_feature: Sets the feature on which neighbor similarity will be determined.
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
            
        covariances = kwargs.get("covariances", None)
        correlation = kwargs.get("correlation", None)


        if kwargs.get("neighbor_similarity", False):
            neighbor_similarity_concentration = kwargs.get("neighbor_similarity_concentration", 30)
            allow_inverse_concentration = kwargs.get("allow_inverse_concentration", False)
            if neighbor_similarity_concentration <= 2 and not allow_inverse_concentration:
                raise ValueError("neighbor_similarity_concentration must be greater than 2 to maintain single-peaked distribution. Set 'allow_inverse_concentration' to True to override.")
            elif neighbor_similarity_concentration <= 0:
                raise ValueError("neighbor_similarity_concentration must be greater than  0.")
                
            neighbor_similarity_strength = kwargs.get("neighbor_similarity_strength", 0)
            if neighbor_similarity_strength < 0:
                raise ValueError("neighbor_similarity_strength cannot be negative (to avoid negative choice weights). Try 0 < neighbor_similarity_concentration < 2 instead for anticoordination with neighbors.")
        
            neighbor_similarity_feature = kwargs.get("neighbor_similarity_feature", "f01")

            postprocessing_iterations = kwargs.get("neighbor_similarity_postprocessing", 30)
        else:
            neighbor_similarity_concentration = kwargs.get("neighbor_similarity_concentration", 30)
            allow_inverse_concentration = kwargs.get("allow_inverse_concentration", False)
            if neighbor_similarity_concentration <= 2 and not allow_inverse_concentration:
                raise ValueError("neighbor_similarity_concentration must be greater than 2 to maintain single-peaked distribution. Set 'allow_inverse_concentration' to True to override.")
            elif neighbor_similarity_concentration <= 0:
                raise ValueError("neighbor_similarity_concentration must be greater than  0.")
                
            neighbor_similarity_strength = kwargs.get("neighbor_similarity_strength", 0)
            if neighbor_similarity_strength < 0:
                raise ValueError("neighbor_similarity_strength cannot be negative (to avoid negative choice weights). Try 0 < neighbor_similarity_concentration < 2 instead for anticoordination with neighbors.")
        
            neighbor_similarity_feature = kwargs.get("neighbor_similarity_feature", "f01")

            postprocessing_iterations = kwargs.get("neighbor_similarity_postprocessing", 0)                      
            
        # Generate feature values
        if covariances is None:
            if correlation is None:
                correlation = 0
                if num_features > 0:
                    warnings.warn("Neither covariance matrix nor correlation specified, using r = 0 as default")
            covariances = []
            for i in range(num_features):
                covariances.append([correlation if not i == j else 1 for j in range(num_features)])
        
        n_agents = len(network.nodes)
     
        feature_values = generate_correlated_continuous_attributes(num_features, (n_agents), covariances, distribution)
        
        # Define feature names
        feature_names = ['f' + str("%02d" % (feature_num + 1)) for feature_num in range(num_features)]   
        
        # Assign attribute valuees to agents
        # If neighbor influence is greater than 0, add network similarity             
        if neighbor_similarity_strength == 0:
            for node_num, node in enumerate(network.nodes):
                for feature_num, feature in enumerate(feature_names):
                    network.nodes[node][feature] = feature_values[node_num, feature_num]
        else:
            apply_neighbor_similarity_beta_weights(network, feature_values, feature_names, neighbor_similarity_feature, neighbor_similarity_concentration, neighbor_similarity_strength)

        if postprocessing_iterations == 'convergence' or postprocessing_iterations > 0:
            dissimilarity_criterion = kwargs.get("neighbor_similarity_criterion", 0.75)
            similarity_postprocessor = SimilarityPostprocessor(network, dissimilarity_criterion, feature_names, neighbor_similarity_feature)
            similarity_postprocessor.create_dissimilarity_data()
            similarity_postprocessor.process(postprocessing_iterations)                     