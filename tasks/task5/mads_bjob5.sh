#!/bin/sh

#BSUB -q hpc
#BSUB -J generate_batch_5
#BSUB -n 32
#BSUB -M 5GB
#BSUB -u s216143@dtu.dk
#BSUB -N 
#BSUB -R "rusage[mem=4GB]"
#BSUB -R "span[hosts=1]"
#BSUB -W 00:30
#BSUB -o Output_%J.out 
#BSUB -e Output_%J.err 


source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613

python mads_simulate_5.py 15