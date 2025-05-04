#!/bin/bash
#BSUB -J task6
#BSUB -q hpc
#BSUB -W 180
#BSUB -R "rusage[mem=2GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n 32
#BSUB -o task6_%J.out
#BSUB -e task6_%J.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -R "select[model == XeonGold6226R]"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613

python simulate_6.py 100