#!/bin/bash
#BSUB -J task7
#BSUB -q hpc
#BSUB -W 00:30
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o task7_%J.out
#BSUB -e task7_%J.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -R "select[model == XeonGold6226R]"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613
time python simulate_7.py 20