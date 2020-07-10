from defSim.Experiment import Experiment

experiment = Experiment(stop_condition="strict_convergence",
                        repetitions=2,
                        attribute_parameters={"num_traits": [i for i in range(5,10)]})
experiment.run_on_cluster()