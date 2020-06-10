Agent attributes (initialization component)
=======================================================

This component is concerned with initializing the attributes of the agents at the start of the simulation run. The following methods are available:

.. toctree ::
   
   Random Categorical Initializer <defSim.agents_init.RandomCategoricalInitializer>
   Random Continuous Initializer <defSim.agents_init.RandomContinuousInitializer>
   Correlated Continuous Initializer <defSim.agents_init.CorrelatedContinuousInitializer>

Initializing the attributes can be done using the following function:

initialize_attributes
-------------------------------------------------------

.. automodule:: defSim.agents_init.agents_init.initialize_attributes
    :undoc-members:
    :show-inheritance:

--------------------------------------------------------

**Some useful methods when programming your own attribute initializer:**

set_categorical_attribute
-------------------------------------------------------

.. automodule:: defSim.agents_init.agents_init.set_categorical_attribute

set_continuous_attribute
-------------------------------------------------------

.. automodule:: defSim.agents_init.agents_init.set_continuous_attribute

Abstract Base Class (ABC)
-------------------------------------------------------

The Abstract Base Class of the agent attribute initializer:

.. automodule:: defSim.agents_init.agents_init.AttributesInitializer
    