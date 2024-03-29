================
Modules overview
================

When using defSim 'out of the box', the modules and tests are called in a fixed
sequence. The Simulation class takes care of this sequence even when the user
calls the Experiment function. In fact, the Experiment class can be seen as a
wrapper of the Simulation class that creates and runs the set of Simulation
models required by the combination of lists of arguments provided by the user.

The relationship between the classes and modules, and the arguments that are
passed on between them are visualized here:

.. image:: fig/defSim-interface.png
  :width: 600
  :alt: defSim workflow

................................................................................

Core modules
############

The core models fall apart into two categories. The 'init' modules take care of
initializing the agents and their structural relationships. The 'sim' modules are
called during the simulation to facilitate their interaction and the roles of the
agents within the interaction.

network_init
------------

agents_init
-----------

focal_agent_sim
---------------

neighbor_selector_sim
---------------------

influence_sim
-------------

................................................................................

Other modules
#############

dissimilarity_calculator
------------------------

tools
-----

network_evolution_sim
---------------------


