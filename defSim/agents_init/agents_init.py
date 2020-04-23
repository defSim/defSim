import networkx as nx
import numpy as np
try:
    import scipy.stats as stats
except ModuleNotFoundError:
    pass
from abc import ABC, abstractmethod
import random
import math
import statistics
import warnings


class AttributesInitializer(ABC):
    """
    Initializes and changes attributes of nodes in the network.
    """

    @staticmethod
    @abstractmethod
    def initialize_attributes(network: nx.Graph, **kwargs):
        """
        Gives initial values to the nodes in the network. Values could e.g. be based on their position in the network.

        :param network: The network that will be modified.
        :param kwargs: This dictionary contains all the implementation-specific parameters.
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
    
    if not distribution in ["uniform", "gaussian"]:
        raise NotImplementedError("The selected distribution has not been implemented. Select from: ['uniform', 'gaussian'].")

    
    means = [0 for _ in range(n_attributes)]
    
    if distribution == "uniform":
        # adjust covariances/correlations for loss expected from transforming to uniform distributions
        for row_index, row in enumerate(covariances):
            for column_index, column in enumerate(row):
                if not row_index == column_index:
                    covariances[row_index, column_index] = 2 * math.sin(math.pi * covariances[row_index, column_index] / 6)

    base_data = np.transpose(np.random.multivariate_normal(mean = means, cov = covariances, size = n_values))

    if distribution == "gaussian":
        final_attributes = np.apply_along_axis(rescale_attribute, axis = 1, arr = base_data)    
    elif distribution == "uniform":
        try:
            # first try scipy.stats vectorized normal cdf function (fastest)
            final_attributes = np.apply_along_axis(stats.norm.cdf, axis = 1, arr = base_data)
        except NameError:
            # if this function cannot be found (scipy not available)
            # try statistics.NormDist().cdf (available from Python 3.8) (slower)
            try:
                final_attributes = np.apply_along_axis(np.vectorize(statistics.NormDist().cdf), axis = 1, arr = base_data)
            except AttributeError:
                # if statistics.NormDist cannot be found (Python < 3.8)
                # define own normalcdf function for standard normal distribution (slowest)
                def normcdf(x):
                    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
                final_attributes = np.apply_along_axis(np.vectorize(normcdf), axis = 1, arr = m)
    
    
    return final_attributes        


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
    adds a possibly multidimensional attribute to all nodes in a network.
    The values of the attribute are drawn from a distribution that is set by the user.

    :param network: The graph object whose nodes' attributes are modified.
    :param shape: sets the output shape of the attribute value. Allows e.g. for multidimensional opinion vectors
    :param name: the name of the attribute. This is used as a key to call the attribute value in other functions
    :param distribution: "gaussian", "exponential", "beta" are possible distributions to choose from
    :param kwargs: a dictionary containing the parameter name and value for each distribution, these are: \n
        loc, scale for gaussian \n
        scale for exponential \n
        a, b for the beta distribution \n
    """
    # todo: decide whether these functions should also be able to be applied to single nodes
    # todo: decide which distributions are possible

    if not distribution in ["uniform"]:
        raise NotImplementedError("The selected distribution has not been implemented. Select from: [uniform].")

    if distribution == "uniform":
        try:
            feature_bounds = kwargs['feature_bounds']
        except KeyError as e:
            raise KeyError('Creating features with continuous random uniform distribution requires feature_bounds to set min and max value') from e

        for i in network.nodes():  # iterate over all nodes
            network.nodes[i][name] = random.uniform(feature_bounds['min'], feature_bounds['max'])  # initialize the feature's value


def initialize_attributes(network: nx.Graph, realization: str, **kwargs):
    """
    This function works as a factory method for the AttributesInitializer component.
    It calls the initialize_attributes function of a specific implementation of the AttributesInitializer and passes to it
    the kwargs dictionary.

    :param network: The network that will be modified.
    :param realization: The specific AttributesInitializer that shall be used to initialize the attributes. Options are "random", ..
    :param kwargs: The parameter dictionary with all optional parameters.
    """
    from . import RandomContinuousInitializer
    from . import RandomCategoricalInitializer

    if realization == "random_categorical":
        RandomCategoricalInitializer.RandomCategoricalInitializer.initialize_attributes(network, **kwargs)
    elif realization == "random_continuous":
        RandomContinuousInitializer.RandomContinuousInitializer.initialize_attributes(network, **kwargs)
    else:
        raise ValueError("Can only select from the options ['random_categorical', 'random_continuous']")
