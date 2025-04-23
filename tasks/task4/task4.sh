#!/bin/bash
#BSUB -J task4
#BSUB -q hpc
#BSUB -W 10
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o ../batch-output/task4_%J.out
#BSUB -e ../batch-output/task4_%J.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -R "select[model == XeonGold6226R]"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613
# Some command...