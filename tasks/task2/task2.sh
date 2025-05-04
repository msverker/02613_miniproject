#!/bin/bash
#BSUB -J task2
#BSUB -q hpc
#BSUB -W 10
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o task2_%J.out
#BSUB -e task2_%J.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -R "select[model == XeonGold6226R]"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613
time python simulate.py 15