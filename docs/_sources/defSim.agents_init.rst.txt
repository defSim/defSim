Agent attributes (initialization component)
=======================================================

This component is concerned with initializing the attributes of the agents at the start of the simulation run. The following methods are available:

.. toctree ::
   
   Random Categorical Initializer <defSim.agents_init.RandomCategoricalInitializer>
   Random Continuous Initializer <defSim.agents_init.RandomContinuousInitializer>
   Correlated Continuous Initializer <defSim.agents_init.CorrelatedContinuousInitializer>

Initializing the attributes can be done using the following function:

This component is concerned with initializing agent attributes at the start of the simulation. The following methods are available:

.. toctree ::
   
   Random Categorical Initializer <defSim.agents_init.RandomCategoricalInitializer>
   Random Continuous Initializer <defSim.agents_init.RandomContinuousInitializer>
   Correlated Continuous Initializer <defSim.agents_init.CorrelatedContinuousInitializer>


initialize_attributes
-------------------------------------------------------

To initialize attributes, the following function can be called:

.. automodule:: defSim.agents_init.agents_init
    :members: initialize_attributes
    :undoc-members:
    :show-inheritance:
    
set_categorical_attribute
-------------------------------------------------------

.. automodule:: defSim.agents_init.agents_init
    :members: set_categorical_attribute

set_continuous_attribute
-------------------------------------------------------

.. automodule:: defSim.agents_init.agents_init
    :members: set_continuous_attribute

Abstract Base Class
-------------------------------------------------------

The Abstract Base Class of the agent attribute initializer:

.. automodule:: defSim.agents_init.agents_init
    :members: AttributesInitializer
    
