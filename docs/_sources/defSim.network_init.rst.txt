Network (network_init)
======================================

This page lists all the functions involved in generating the NetworkX Graph object. Most notably 'generate_network' is
the factory method that you should call to produce a network from scratch, and 'read_network' is the function you should
call when you want to produce a network from an adjacency matrix or edgelist.

generate_network
----------------------------------------------------

.. automodule:: defSim.network_init.network_init
    :members: generate_network

read_network
----------------------------------------------------

.. automodule:: defSim.network_init.network_init
    :members: read_network
    
network_generators
----------------------------------------------------

.. automodule:: defSim.network_init.network_init
    :members: _produce_grid_network, _produce_ring_network, _produce_spatial_random_graph, _produce_networkx_graph
    
execute_ms_rewiring
----------------------------------------------------

.. automodule:: defSim.network_init.network_init
    :members: execute_ms_rewiring