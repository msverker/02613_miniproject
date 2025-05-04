#!/bin/sh

#BSUB -q hpc
#BSUB -J generate_batch_5
#BSUB -n 32
#BSUB -M 2GB
#BSUB -u s216143@dtu.dk
#BSUB -N 
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -W 05:00
#BSUB -o Output_%J.out 
#BSUB -e Output_%J.err 
#BSUB -R "select[model == XeonGold6226R]"


source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613

time python simulate_5.py 100