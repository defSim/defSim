import networkx as nx
import numpy as np
import scipy.stats as stats
import math
import warnings
import random
from .agents_init import AttributesInitializer
from .agents_init import generate_correlated_continuous_attributes


class CorrelatedContinuousInitializer(AttributesInitializer):
    """
    Implements the AttributesInitializer as a random initialization of correlated random continuous features.
    """

    def __init__(self, distribution: str = 'uniform', **kwargs):
        """
        :param str='uniform' distribution: Type of continuous distribution to draw feature values from.
        :param bool=False neighbor_similarity: If set to True, a default application of neighbor similarity is used. Regardless of the value of this parameter, similarity options can always be customized individually
        :param float=10 neighbor_similarity_concentration: How closely concentrated (peaked) the weight distribution is around the mean value of neighbors (minimum value > 2 required to maintain integrity of the distribution)
        :param float=0 neighbor_similarity_strength: Strength of weighting by neighbor value. 0 = no influence of neighbors
        :param int=1 num_features: How many different attributes each node has.
        :param str='f01' neighbor_similarity_feature: Sets the feature on which neighbor similarity will be determined.
        :param [list] or numpy.array covariances: Complete covariance matrix (see agents_init.generate_correlated_continuous_attributes)
        :param float correlation: Single correlation value to apply to all pairs of attributes
        :param bool allow_inverse_concentration: Use to allow concentrations below 2, which result in anticoordination with neighbors
        :param str or int neighbor_similarity_postprocessing: Sets the number of postprocessing iterations (integer to set max number of iterations, 'convergence' to not set a maximum)
        :param float neighbor_similarity_criterion: Maximum allowable dissimilarity to neighbors during postprocessing
        """
        
        # Check inputs
        if not distribution in ["uniform", "normal"]:
            raise NotImplementedError("The selected distribution has not been implemented. Select from: [uniform, normal].")
        self.distribution = distribution

        try:
            self.num_features = kwargs["num_features"]
        except KeyError:
            warnings.warn("Number of features not specified, using 1 as default")
            self.num_features = 1

        self.covariances = kwargs.get("covariances", None)
        self.correlation = kwargs.get("correlation", None)    

        self.neighbor_similarity = kwargs.get("neighbor_similarity", False)
        if self.neighbor_similarity:
            self.neighbor_similarity_concentration = kwargs.get("neighbor_similarity_concentration", 30)
            self.allow_inverse_concentration = kwargs.get("allow_inverse_concentration", False)
            if self.neighbor_similarity_concentration <= 2 and not self.allow_inverse_concentration:
                raise ValueError(
                    "neighbor_similarity_concentration must be greater than 2 to maintain single-peaked distribution. Set 'allow_inverse_concentration' to True to override.")
            elif self.neighbor_similarity_concentration <= 0:
                raise ValueError("neighbor_similarity_concentration must be greater than  0.")

            self.neighbor_similarity_strength = kwargs.get("neighbor_similarity_strength", 0)
            if self.neighbor_similarity_strength < 0:
                raise ValueError(
                    "neighbor_similarity_strength cannot be negative (to avoid negative choice weights). Try 0 < neighbor_similarity_concentration < 2 instead for anticoordination with neighbors.")

            self.neighbor_similarity_feature = kwargs.get("neighbor_similarity_feature", "f01")

            self.postprocessing_iterations = kwargs.get("neighbor_similarity_postprocessing", 30)
        else:
            self.neighbor_similarity_concentration = kwargs.get("neighbor_similarity_concentration", 30)
            self.allow_inverse_concentration = kwargs.get("allow_inverse_concentration", False)
            if self.neighbor_similarity_concentration <= 2 and not self.allow_inverse_concentration:
                raise ValueError(
                    "neighbor_similarity_concentration must be greater than 2 to maintain single-peaked distribution. Set 'allow_inverse_concentration' to True to override.")
            elif self.neighbor_similarity_concentration <= 0:
                raise ValueError("neighbor_similarity_concentration must be greater than  0.")

            self.neighbor_similarity_strength = kwargs.get("neighbor_similarity_strength", 0)
            if self.neighbor_similarity_strength < 0:
                raise ValueError(
                    "neighbor_similarity_strength cannot be negative (to avoid negative choice weights). Try 0 < neighbor_similarity_concentration < 2 instead for anticoordination with neighbors.")

            self.neighbor_similarity_feature = kwargs.get("neighbor_similarity_feature", "f01")

            self.postprocessing_iterations = kwargs.get("neighbor_similarity_postprocessing", 0)    

        self.dissimilarity_criterion = kwargs.get("neighbor_similarity_criterion", 0.75)

    def initialize_attributes(self, network: nx.Graph, **kwargs):
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

        Regardless of whether this non-random distribution has been applied, a minimum level of similarity between neighbors can be
        enforced by applying a postprocessing procedure which moves nodes whose dissimilarity to neighbors exceeds the value specified as
        'neighbor_similarity_criterion'. Postprocessing can be enabled either running to convergence using 'neighbor_similarity_postprocessing': 'convergence',
        or to a maximum number of iterations (if convergence is not reached sooner) using 'neighbor_similarity_postprocessing': int.

        For a basic neighbor similarity approach where only postprocessing is applied, with a maximum of 10 iterations and a dissimilarity criterion of 0.75,
        set 'neighbor_similarity' to True and don't make further adjustments. For custom setups, you can select any combination of weighted distribution
        and postprocessing by setting the relevant parameters.

        :param network: The graph object whose nodes' attributes are modified.
        """

        # Generate feature values
        if self.covariances is None:
            if self.correlation is None:
                self.correlation = 0
                if self.num_features > 0:
                    warnings.warn("Neither covariance matrix nor correlation specified, using r = 0 as default")
            self.covariances = []
            for i in range(self.num_features):
                self.covariances.append([self.correlation if not i == j else 1 for j in range(self.num_features)])

        n_agents = len(network.nodes)

        feature_values = generate_correlated_continuous_attributes(self.num_features, (n_agents), self.covariances, self.distribution)

        ## the code beyond this point only works with values ranging between 0 and 1
        if (np.amin(feature_values) < 0) or (np.amax(feature_values) > 1):
            raise ValueError('Attribute values outside range [0,1] not supported. Rescale first.')

            # Define feature names
        feature_names = ['f' + str("%02d" % (feature_num + 1)) for feature_num in range(self.num_features)]

        # Assign attribute values to agents
        for node_num, node in enumerate(network.nodes):
            for feature_num, feature in enumerate(feature_names):
                network.nodes[node][feature] = feature_values[node_num, feature_num]

        # If neighbor influence is greater than 0, add network similarity
        if self.neighbor_similarity_strength > 0:
            apply_neighbor_similarity_beta_weights(network, feature_values, feature_names, self.neighbor_similarity_feature,
                                                   self.neighbor_similarity_concentration, self.neighbor_similarity_strength)

        if self.postprocessing_iterations == 'convergence' or self.postprocessing_iterations > 0:            
            similarity_postprocessor = SimilarityPostprocessor(network, self.dissimilarity_criterion, feature_names,
                                                               self.neighbor_similarity_feature)
            similarity_postprocessor.process(self.postprocessing_iterations)


def apply_neighbor_similarity_beta_weights(network, feature_values, feature_names, neighbor_similarity_feature,
                                           neighbor_similarity_concentration, neighbor_similarity_strength):
    """
    Distributes feature values across nodes in a network in a non-random way. The method starts by creating a random
    distribution and then redistributes semi-randomly by weighting the average attribute values of neighbors values.
    """
    similarity_feature_col = feature_names.index(neighbor_similarity_feature)

    ## first initialize all features for all nodes
    for node in network.nodes:
        for feature in feature_names:
            network.nodes[node][feature] = None        

    ## sort features by first column (first feature)
    sorted_indexes = np.argsort(feature_values[:, similarity_feature_col])
    sorted_features = feature_values[sorted_indexes]
    
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
    """
    This class holds functions to perform postprocessing on (correlated) features with the goal of
    enforcing a minimum level of similarity among neighbors. The main parameter to set here is the
    dissimilarity criterion. The dissimilarity cirterion works by setting a limit on the maximum
    dissimilarity between neighbors on the neighbor_similarity_feature.
    """

    def __init__(self, network: nx.Graph, dissimilarity_criterion: float, feature_names: list,
                 neighbor_similarity_feature: str):
        """
        :param nx.Graph network: The graph object whose nodes' attributes are modified.
        :param float dissimilarity_criterion: maximum allowable attribute value distance between neighbors.
        :param list feature_names: List of all feature names as strings
        :param str neighbor_similarity_feature: Name of feature on which neighbor similarity is to be enforced
        """        
        self.network = network
        self.dissimilarity_criterion = dissimilarity_criterion
        self.feature_names = feature_names
        self.neighbor_similarity_feature = neighbor_similarity_feature
        self.set_constant_count = 0
        self.constant_num_dissimilar_count = 0


    def dissimilarity_data_for_node(self, node: str):
        """
        Looks up the neighbors of a given node in the current network, and finds the maximum 
        dissimilarity. Returns the node identifier, maximum dissimilarity, and the node's own value
        on the similarity feature.
        :param str node: Node identifier to look up in the network
        :returns list: node identifier, maximum observed dissimilarity to neighbors, node's own attribute value
        """
        neighbor_values = [self.network.nodes[neighbor][self.neighbor_similarity_feature] for neighbor in self.network.neighbors(node)]
        node_value = self.network.nodes[node][self.neighbor_similarity_feature]
        max_dissimilarity = max([abs(neighbor_val - node_value) for neighbor_val in neighbor_values])

        return [node, max_dissimilarity, node_value]

    def create_dissimilarity_data(self):
        """
        Finds the dissimilarity data for each node in the network and stores data for all nodes
        as a numpy array. 
        """
        nodes = list(self.network.nodes)

        # go through list once
        dissimilarity_data = []
        for node in nodes:
            dissimilarity_data.append(self.dissimilarity_data_for_node(node))

        self.dissimilarity_data = np.array(dissimilarity_data)                 

    def update_dissimilarity(self, node1: str, node2: str):
        """
        For two given nodes, and all their neighbors, recalculate dissimilarity data. Use after swapping nodes to bring
        data up to date with new network position. The stored dissimilarity data is modified in place.
        :param str node1: Node identifier for first node
        :param str node2: Node identifier for second node
        """
        node1_neighbors = self.network.neighbors(node1)
        node2_neighbors = self.network.neighbors(node2)

        self.dissimilarity_data[np.where(self.dissimilarity_data[:,0] == node1)] = self.dissimilarity_data_for_node(node1)
        self.dissimilarity_data[np.where(self.dissimilarity_data[:,0] == node2)] = self.dissimilarity_data_for_node(node2)                

        for neighbor in node1_neighbors:
             self.dissimilarity_data[np.where(self.dissimilarity_data[:,0] == neighbor)] = self.dissimilarity_data_for_node(neighbor)

        for neighbor in node2_neighbors:
             self.dissimilarity_data[np.where(self.dissimilarity_data[:,0] == neighbor)] = self.dissimilarity_data_for_node(neighbor)          

    def improvement_if_swapped(self, node1_data, node2_data):
        """
        Check whether dissimilarity in the network would be improved if two given nodes are swapped. 
        First, attribute values for each node's neighbors are gathered.
        Then, dissimilarity is calculated as if the two nodes swapped position. 
        Then, improvement is checked by comparing the total dissimilarity in the current position to the total
        dissimilarity in the new positions. The idea is that a swap is not an improvement if reducing dissimilarity
        for one node means increaing dissimilarity for the other node more. More weight is given to large 
        dissimilarities by squaring all absolute dissimilarity values.

        :param node1_data: row from the np.array containing dissimilarity data. Contains node identifier, current dissimilarity and
            attribute value for the first node
        :param node2_data: row from the np.array containing dissimilarity data. Contains node identifier, current dissimilarity and
            attribute value for the second node
        :returns bool: True if swapping these nodes would improve dissimilarity, else false
        """
        current_dissimilarity_node1 = node1_data[1]
        current_dissimilarity_node2 = node2_data[1]

        value_node1 = node1_data[2] 
        value_node2 = node2_data[2]

        neighbor_values_node1 = [self.network.nodes[neighbor][self.neighbor_similarity_feature] for neighbor in self.network.neighbors(node1_data[0])]
        neighbor_values_node2 = [self.network.nodes[neighbor][self.neighbor_similarity_feature] for neighbor in self.network.neighbors(node2_data[0])]

        new_dissimilarity_node1 = max([abs(neighbor_val - value_node1) for neighbor_val in neighbor_values_node2])
        new_dissimilarity_node2 = max([abs(neighbor_val - value_node2) for neighbor_val in neighbor_values_node1])

        return (current_dissimilarity_node1**2 + current_dissimilarity_node2**2) - (new_dissimilarity_node1**2 + new_dissimilarity_node2**2)

    def swap_nodes(self, node1: str, node2: str):
        """
        Swap attribute values for two network nodes. (Effectively swapping the network position of two agents.)
        :param str node1: Node identifier for first node
        :param str node2: Node identifier for second node
        """
        for feature_name in self.feature_names:
            node1_old_value = self.network.nodes[node1][feature_name]
            node2_old_value = self.network.nodes[node2][feature_name]
            self.network.nodes[node1][feature_name] = node2_old_value
            self.network.nodes[node2][feature_name] = node1_old_value             
 
    def swap_dissimilar_nodes(self):
        """
        Finds nodes in the network whose dissimilarity to neighbors on the neighbor similarity feature exceeds the
        dissimilarity criterion, and swaps these nodes if swapping would improve dissimilarity. 
        Tracks the number of swaps made. 
        :returns tuple: Number of swaps made, np.array containing data for all nodes which exceeded dissimilarity criterion
        """

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

                self.swap_nodes(dissimilar_node[0], other_node[0])
                self.update_dissimilarity(dissimilar_node[0], other_node[0])
                swaps += 1

        return (swaps, too_dissimilar_nodes)

    def check_convergence(self, swaps, current_dissimilar_nodes, nodes_involved_previous, num_dissimilar_previous):
        """
        Checks whether the postprocessing procedure has converged. If convergence is detected but there are still agents
        who are too dissimilar from their neighbor according to the dissimilarity criterion, a warning is given.
        Convergence is detected when:
        - no swaps were made and no nodes are too dissimilar OR
        - no swaps were made but there are still some nodes too dissimilar --> warning OR
        - the set of agents who ware too dissimilar has not changed for 10 iterations --> warning OR
        - the set of agents who are too dissimilar is not constant but the number of agents too dissimilar has not changed
            for 50 iterations --> warning

        :returns bool: True if one of the convergence conditions detected, else false.

        """

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

    def process(self, postprocessing_iterations: str or int): 
        """
        Apply the postprocessing procedure to a network. Postprocessing can either run to convergence or to a maximum
        number of iterations. Even if a maximum number of iterations is set, convergence will still end postprocessing.

        :param str or int postprocessing_iterations: Maximum number of postprocessing iterations (int) or 'convergence'
            to run without limiting maximum number of iterations
        """

        iteration = 0
        num_dissimilar_previous = 0
        nodes_involved_previous = []
        self.set_constant_count = 0
        self.constant_num_dissimilar_count = 0

        self.create_dissimilarity_data()

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
