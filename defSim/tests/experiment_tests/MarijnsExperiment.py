from defSim.Experiment import Experiment
import os

if __name__ == '__main__':
    experiment = Experiment(communication_regime=["one-to-one", "one-to-many"],
                            attribute_parameters={"num_features": [i for i in range(5,10)],
                                                  "num_traits": [i for i in range(2,22,2)]},
                            stop_condition="strict_convergence",
                            repetitions=100)

    results = experiment.run(parallel=True)

    with open("MarijnsExperiment.csv", "w+") as output_file:
        results.to_csv(output_file, sep=";", index=False)
    print("results written to: %s" % os.path.abspath("MarijnsExperiment.csv"))


