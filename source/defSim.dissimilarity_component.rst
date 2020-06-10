Dissimilarity component
==========================================

The dissimilarity component handles calculating the dissimilarity between agents before and during the simulation run.
Each method should contain a function ``calculate_dissimilarity`` to calculate dissimilarity between two agents and a
function ``calculate_dissimilarity_networkwide`` to calculate dissimilarity at the start of the simulation run.

.. toctree::
   Euclidean Distance <defSim.dissimilarity_component.EuclideanDistance>
   Hamming Distance <defSim.dissimilarity_component.HammingDistance>

select_calculator
---------------------------------------------------

.. automodule:: defSim.dissimilarity_component.dissimilarity_calculator
    :members: select_calculator

--------------------------------------------------------

**Some useful methods when programming your own dissimilarity measure:**

Abstract Base Class (ABC)
-------------------------------------------------------

The Abstract Base Class of the dissimilarity component:

.. automodule:: defSim.dissimilarity_component.dissimilarity_calculator
    :members: DissimilarityCalculator
