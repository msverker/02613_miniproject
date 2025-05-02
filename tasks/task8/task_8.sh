#!/bin/bash
#BSUB -J taks_8
#BSUB -q c02613
#BSUB -W 30
#BSUB -R "rusage[mem=8GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n 4
#BSUB -o task8_%J.out
#BSUB -e task8_%J.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -gpu "num=1:mode=exclusive_process"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613

echo "OLD"
time python simulate_8_old.py 100

echo "NEW"
time python simulate_8_new.py 100