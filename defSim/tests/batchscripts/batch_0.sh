#!/bin/bash
#SBATCH --job-name=simulation_chunk_0.job
#SBATCH --output=output/chunk0.txt
#SBATCH --time=30:00
#SBATCH --mem=8000
#SBATCH --partition=short
#SBATCH --cpus-per-task=24
python /home/dieko/VENVs/defSim/lib/python3.6/site-packages/defSim/tools/ClusterExecutionScript.py 0 /home/dieko/Documents/defSim/defSim/tests/pickles /home/dieko/Documents/defSim/defSim/tests/output
