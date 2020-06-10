Neighbor selector (simulation component)
=======================================================

This component is concerned with selecting the neighbor of the focal agent (i.e. the agent who receives the focal
agent's attribute value) at each timestep in the simulation run.

The following methods are available:

.. toctree::
   Random Neighbor Selector <defSim.neighbor_selector_sim.RandomNeighborSelector>
   Similar Neighbor Selector <defSim.neighbor_selector_sim.SimilarNeighborSelector>

neighbor_selector_sim module
-------------------------------------------------------

.. automodule:: defSim.neighbor_selector_sim.neighbor_selector_sim
    :members: select_neighbors
    :undoc-members:
    :show-inheritance:

-------------------------------------------------------

Abstract Base Class (ABC)
-------------------------------------------------------

.. automodule:: defSim.neighbor_selector_sim.neighbor_selector_sim
    :members: NeighborSelector
    :undoc-members:
    :show-inheritance: