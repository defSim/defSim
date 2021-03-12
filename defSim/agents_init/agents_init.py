import networkx as nx
import numpy as np
import scipy.stats as stats
from abc import ABC, abstractmethod
import random
import math
import statistics
import warnings
import inspect


class AttributesInitializer(ABC):
    """
    Initializes and changes attributes of nodes in the network.
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: This dictionary contains all the implementation-specific parameters.
        """
        pass

    @abstractmethod
    def initialize_attributes(self, network: nx.Graph, **kwargs):
        """
        Gives initial values to the nodes in the network. Values could e.g. be based on their position in the network.

        :param network: The network that will be modified.
        """
        pass

def rescale_attribute(attribute: list, min_value: float = 0, max_value: float = 1) -> list:
    """
    Rescale any attribute to a fixed range of values, [0, 1] by default.
    Preserves the shape of the distribution.
    :param list attribute: all values on an attribute to rescale
    :param float min_value: lowest allowed value for rescaled attribute
    :param float max_value: highest allowed value for rescaled attribute
    :returns list: rescaled attribute     
    """
    
    max_observed = max(attribute)
    min_observed = min(attribute)
    observed_range = max_observed - min_observed
    desired_range = max_value - min_value
    
    return [((value - min_observed) / observed_range) * desired_range + min_value for value in attribute]


def generate_correlated_continuous_attributes(n_attributes: int, n_values: int, covariances: [list] or np.array, distribution: str = "uniform", **kwargs) -> list:
    """
    Generate multiple correlated attribute vectors.
    The values of the attribute are drawn from a distribution that is set by the user.
    The covariance matrix determines the generated correlations. 
    The covariance matrix must be completely specified. Base distribution for the attributes is always a
    multivariate random normal distribution, which assumes mean 0 and standard deviation 1. As a result, 
    covariances and correlations are equal. You can thus enter the desired correlations in the covariance
    matrix.
    :param int n_attributes: number of attributes to generate
    :param int n_values: number of values to generate in each attribute
    :param [list] or numpy.array covariances: complete covariance matrix. Specify the covariance matrix as a numpy array or a list of lists, of n rows and n columns. 
    :param string distribution: "gaussian" and "uniform are currently implemented"
    :param kwargs: a dictionary containing additional parameter values
    """
    
    if not distribution in ["uniform", "normal"]:
        raise NotImplementedError("The selected distribution has not been implemented. Select from: ['uniform', 'gaussian'].")

    if not isinstance(covariances, np.ndarray):
        covariances = np.array(covariances)

    try:
        rng = kwargs["np_random_generator"]
    except KeyError:
        warnings.warn("No Numpy Generator in parameter dictionary, creating default")
        rng = np.random.default_rng()
    
    means = [0 for _ in range(n_attributes)]
    
    if distribution == "uniform":
        # adjust covariances/correlations for loss expected from transforming to uniform distributions
        for row_index, row in enumerate(covariances):
            for column_index, column in enumerate(row):
                if not row_index == column_index:
                    covariances[row_index, column_index] = 2 * math.sin(math.pi * covariances[row_index, column_index] / 6)

    base_data = rng.multivariate_normal(mean = means, cov = covariances, size = n_values)

    if distribution == "gaussian":
        final_attributes = np.apply_along_axis(rescale_attribute, axis = 0, arr = base_data)    
    elif distribution == "uniform":
        final_attributes = np.apply_along_axis(stats.norm.cdf, axis = 0, arr = base_data)    
    
    return final_attributes        


def initialize_attributes(network: nx.Graph, realization: str, **kwargs):
    """
    This function works as a factory method for the AttributesInitializer component.
    It calls the initialize_attributes function of a specific implementation of the AttributesInitializer and passes to it
    the kwargs dictionary.

    :param network: The network that will be modified.
    :param realization: The specific AttributesInitializer that shall be used to initialize the attributes.
      Options are "random_categorical" and "random_continuous".
    :param kwargs: The parameter dictionary with all optional parameters.
    """
    from . import RandomContinuousInitializer
    from . import RandomCategoricalInitializer
    from . import CorrelatedContinuousInitializer

    if realization == "random_categorical":
        RandomCategoricalInitializer.RandomCategoricalInitializer(**kwargs).initialize_attributes(network)
    elif realization == "random_continuous":
        RandomContinuousInitializer.RandomContinuousInitializer(**kwargs).initialize_attributes(network)
    elif realization == 'correlated_continuous':
        CorrelatedContinuousInitializer.CorrelatedContinuousInitializer(**kwargs).initialize_attributes(network)  
    elif isinstance(realization, AttributesInitializer):
        realization.initialize_attributes(network, **kwargs)
    else:
        raise ValueError("Can only select from the options ['random_categorical', 'random_continuous', 'correlated_continuous'] or supply an instance of a class which inherits from the ABC")


def set_categorical_attribute(network: nx.Graph, name: str, values: list, distribution: str = "uniform", **kwargs):
    """
    Adds a categorical attribute to all nodes in a network. The values for that attribute are drawn from a list
    of possible values provided by the user.

    :param network: The graph object whose nodes' attributes are modified.
    :param name: the name of the attribute. This is used as a key to call the attribute value in other functions.
    :param values: A list that contains all possible values for that attribute.
    :param distribution: 'gaussian', 'uniform', or 'custom' are possible values.
    :param kwargs: a dictionary containing the parameter name and value for each distribution, these are: \n
        for gaussian: loc and scale. loc would be the index of the most common value in the values list \n
        for custom distribution: c. an array-like containing the probabilities for each entry in the values list.
    """
    # todo: implement other distributions
    for i in network.nodes():  # iterate over all nodes
        network.nodes[i][name] = random.choice(values)  # initialize the feature's value


def set_continuous_attribute(network: nx.Graph, name: str, shape: tuple = (1), distribution: str = "uniform",
                             **kwargs):
    """
    Adds a continuous attribute to all nodes in a network.
    The values of the attribute are drawn from a distribution that is set by the user.
    Random values are drawn using the numpy.random module.

    :param network: The graph object whose nodes' attributes are modified.
    :param shape: sets the output shape of the attribute value. Allows e.g. for multidimensional opinion vectors
    :param name: the name of the attribute. This is used as a key to call the attribute value in other functions
    :param distribution: "normal", "uniform", "beta", "triangular" are possible distributions to choose from
    :param kwargs: a dictionary containing the parameter name and value for each distribution, these are: \n
        loc, scale to set center and spread for the normal distribution (truncated at [0,1]) \n
        a, b to set center and shape for the beta distribution for the beta distribution \n
        loc to set center for the triangular distribution
    """

    if not distribution in ["uniform", "normal", "beta", "triangular"]:
        raise NotImplementedError("The selected distribution has not been implemented. Select from: [uniform, normal, beta, triangular].")

    try:
        rng = kwargs["np_random_generator"]
    except KeyError:
        warnings.warn("No Numpy Generator in parameter dictionary, creating default")
        rng = np.random.default_rng()

    # NOTE: it would probably be faster to let numpy draw all random values at once, and then assign them
    # that's something we can do if this ever becomes a performance issue (which it likely won't)
    if distribution == "uniform":
        for i in network.nodes():  # iterate over all nodes
            network.nodes[i][name] = rng.uniform(low = 0, high = 1)  # initialize the feature's value

    elif distribution == "normal":
        # with default values loc = 0.5 and scale = 0.2, 
        # approximately 1.2% of generated values will fall outside [0,1]
        # these are set to 0 or 1
        loc = kwargs.get("loc", 0.5)
        scale = kwargs.get("scale", 0.2)
        for i in network.nodes():
            network.nodes[i][name] = min(1, max(0, rng.normal(loc = loc, scale = scale)))

    elif distribution == "beta":
        # with default values a = 3, b = 3, the center of the distribution is at 0.5
        # the distribution is symmetrical, and approximately 50% of all values fall
        # between 0.36 and 0.64
        a = kwargs.get("a", 3)
        b = kwargs.get("b", 3)
        for i in network.nodes():
            network.nodes[i][name] = rng.beta(a = a, b = b)

    elif distribution == "triangular":
        # with default value mode loc = 0.5, the mode of the triangular distribution
        # is at 0.5 and the distribution is symmetrical over the interval [0,1]
        loc = kwags.get("loc", 0.5)
        for i in network.nodes():
            network.nodes[i][name] = rng.triangular(left = 0, mode = loc, right = 1)        