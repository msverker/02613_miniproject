#!/bin/bash
#BSUB -J task5[1,2,3,4,5,8,10,12,14,16,18,20,22,24,26,28,30,32]
#BSUB -q hpc
#BSUB -W 10
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o task5_%J_%I.out
#BSUB -e task5_%J_%I.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -R "select[model == XeonGold6226R]"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613
time python simulate_5.py 1