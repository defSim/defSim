import networkx as nx
from abc import ABC, abstractmethod
import random
import warnings
import inspect


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

    if realization == "random_categorical":
        RandomCategoricalInitializer.RandomCategoricalInitializer.initialize_attributes(network, **kwargs)
    elif realization == "random_continuous":
        RandomContinuousInitializer.RandomContinuousInitializer.initialize_attributes(network, **kwargs)
    elif inspect.isclass(realization):
        realization.initialize_attributes(network, **kwargs)
    else:
        raise ValueError("Can only select from the options ['random_categorical', 'random_continuous'] or supply a realization of the ABC")


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



