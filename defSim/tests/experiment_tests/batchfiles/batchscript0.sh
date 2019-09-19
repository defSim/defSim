#!/bin/bash
#SBATCH --job-name=simulation_chunk_0.job
#SBATCH --output=output\chunk0.txt
#SBATCH --time=30:00
#SBATCH --mem=8000
#SBATCH --partition=short
#SBATCH --cpus-per-task=24
python C:\Users\Anton Laukemper\Desktop\Uni\SS19\Research Internship\defSim\defSim_src\tools\runSimulationParallely.py 0 C:\Users\Anton Laukemper\Desktop\Uni\SS19\Research Internship\defSim\defSim_src\tests\experiment_tests\pickles C:\Users\Anton Laukemper\Desktop\Uni\SS19\Research Internship\defSim\defSim_src\tests\experiment_tests\output
