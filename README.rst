defSim
======

.. image:: https://img.shields.io/pypi/v/defsim.svg
   :target: https://pypi.org/project/defsim/

*the discrete event framework for social influence models*

New to defSim? `Learn how to use defSim in this quick introduction <https://defSim.github.io/defSim/Introduction_to_defSim.html>`_ or inspect our example notebooks at `defSim-examples <https://github.com/defSim/defSim-examples>`_.

For a description of all of defSim's functions, see the `documentation <https://defSim.github.io/defSim>`_

How to install defSim
---------------------

To install the package, you can use pip:

.. code-block:: console

   pip install defSim

**For developers**:

Install the current github version using :code:`pip install git+https://github.com/defSim/defSim`
   
Similarly, to update from a previously installed version use :code:`pip install git+https://github.com/defSim/defSim --upgrade`

If you want to edit the code locally, clone the repository to a folder of your choice and execute :code:`pip install .` in that folder. If you change the package or pull changes run :code:`pip install --upgrade .` to update the changes.

Changelog
---------

This project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

**v0.1.3**

* some new output measures have been added: Dispersion, Spread and Coverage
* the Experiment class takes a general parameter_dict dictionary. In the future, supplying the dictionaries
  network_parameters, attribute_parameters, focal_agent_parameters, neighbor_parameters, influence_parameters and
  stop_condition_parameters may be deprecated.

**v0.1.2**

* the wrapper functions Experiment and Simulation accept subclasses of AttributesInitializer,
  FocalAgentSelector, NeighborSelector and InfluenceOperator