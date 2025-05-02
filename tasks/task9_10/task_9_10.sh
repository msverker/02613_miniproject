#!/bin/bash
#BSUB -J taks_9_10
#BSUB -q c02613
#BSUB -W 30
#BSUB -R "rusage[mem=8GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n 4
#BSUB -o task9_10_%J.out
#BSUB -e task9_10_%J.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -gpu "num=1:mode=exclusive_process"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613

echo "9"
time python simulate_9.py 50

echo "10"
time python simulate_10.py 50