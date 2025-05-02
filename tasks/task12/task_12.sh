#!/bin/bash
#BSUB -J taks_12[1-10]
#BSUB -q c02613
#BSUB -W 30
#BSUB -R "rusage[mem=8GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n 4
#BSUB -o task12_%J_%I.out
#BSUB -e task12_%J_%I.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -gpu "num=1:mode=exclusive_process"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613

time python simulate_12.py $LSB_JOBINDEX 10