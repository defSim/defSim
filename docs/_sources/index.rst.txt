.. defSim documentation master file, created by
   sphinx-quickstart on Sat Jun 22 17:14:28 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to defSim's documentation!
==================================

Here you can find the API documentation for the world's first package on social influence simulations.

defSim is a package that aims to be the modular standard for social influence models. With defSim you can run a single :class:`~defSim.Simulation`, execute a larger Simulation :class:`~defSim.Experiment`, or use any number of pre-programmed modules for your own idea or variation of a traditional social influence model. By using defSim you save a lot of time programming functions that you will need in any social influence research project, but furthermore you make sure that your model remains strictly comparable with traditional models and other models in the defSim-realm.

The flow of a single simulation run implemented by defSim looks like this:  

.. image:: fig/defSim-flow.png
  :width: 400
  :alt: defSim workflow

All elements on the left represent the separate modules.

..add explanation on modules and typical workflow

I recommend to start with the :class:`~defSim.Simulation` class and the :class:`~defSim.Experiment` class to understand how to create your own multi-agent system experiment.

Here are some examples of how to create experiments:

.. literalinclude:: examples.py
    :language: python


The package consists of the following components:
-------------------------------------------------

.. toctree::
   
   Quick start guide <quickintro>
   defSim <defSim>
   Networks <defSim.network_init>
   Agent features <defSim.agents_init>
   Focal agent selection <defSim.focal_agent_sim>
   Neighbor selector <defSim.neighbor_selector_sim>
   Influence <defSim.influence_sim>
   Network evolution <defSim.network_evolution_sim>
   Dissimilarity updaters <defSim.dissimilarity_component>
   defSim.tests
   defSim.tools

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
