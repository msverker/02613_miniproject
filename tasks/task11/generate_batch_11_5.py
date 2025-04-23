import os
n_proc_list = [1, 2, 3, 4, 5, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]

def content(n_proc):
    file_content = f"""
#!/bin/bash
#BSUB -J task11_5_{n_proc}
#BSUB -q hpc
#BSUB -W 240
#BSUB -R "rusage[mem=2GB]"
#BSUB -R "span[hosts=1]"
#BSUB -n {n_proc}
#BSUB -o task11_5_%J_%I.out
#BSUB -e task11_5_%J_%I.err
#BSUB -u s214753@dtu.dk
#BSUB -B
#BSUB -N
#BSUB -R "select[model == XeonGold6226R]"

source /dtu/projects/02613_2024/conda/conda_init.sh
conda activate 02613
echo "{n_proc}"
time python simulate_11_5.py 100 {n_proc}
"""
    return file_content

for n_proc in n_proc_list:
    # Make the file
    f = open(f"task11_5_{n_proc}.sh", "w")
    f.write(content(n_proc))
    f.close()

    # Submit the file
    os.system(f"bsub < task11_5_{n_proc}.sh")
