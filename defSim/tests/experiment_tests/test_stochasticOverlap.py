from defSim import Experiment
import timeit
import random

if __name__ == '__main__':
    random.seed("random")
    stochasticOverlapStrict = Experiment.Experiment(communication_regime="one-to-one",
                                   network_parameters={"num_agents": 49},
                                   influence_function="axelrod",
                                   stop_condition="strict_convergence")

    stochasticOverlapPragmatic = Experiment.Experiment(communication_regime="one-to-one",
                                   network_parameters={"num_agents": 49},
                                   influence_function="axelrod",
                                   stop_condition="pragmatic_convergence")

    print("Experiment 1: stochasticOverlap with strict convergence sequential")
    print("10 iterations")
    print("Time: "+str(timeit.timeit(stochasticOverlapStrict.run, number=10)))

    print("Experiment 1: stochasticOverlap with pragmatic convergence sequential")
    print("10 iterations")
    print("Time: "+str(timeit.timeit(stochasticOverlapPragmatic.run, number=10)))
