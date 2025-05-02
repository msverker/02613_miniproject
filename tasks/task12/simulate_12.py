# From simulate_8_new.py
from os.path import join
import sys
import numpy as np
from numba import cuda

@cuda.jit
def jacobi_kernel(u, u_new, mask):
    i = cuda.grid(1) 

    if i < mask.shape[0]:
        i_mask, j_mask = mask[i]
        u_new[i_mask, j_mask] = 0.25 * (u[i_mask, j_mask - 1] + u[i_mask, j_mask + 1] + u[i_mask - 1, j_mask] + u[i_mask + 1, j_mask])


def jacobi(u, interior_mask, num_iter, _):
    mask_idxs = np.stack(np.where(interior_mask), axis=-1).astype(np.int32)
    mask_idxs += 1
    d_u = cuda.to_device(u)
    d_u_new = cuda.to_device(u)
    d_mask_idx = cuda.to_device(mask_idxs)
    
    tpb = 64
    bpg = (mask_idxs.shape[0] + tpb - 1) // tpb
    for i in range(num_iter):
        jacobi_kernel[bpg, tpb](d_u, d_u_new, d_mask_idx)
        d_u, d_u_new = d_u_new, d_u  

    return d_u.copy_to_host()


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }


if __name__ == '__main__':
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    part = int(sys.argv[1]) - 1 # job names cant contain 0 so we subtract 1 :))
    number_of_parts = int(sys.argv[2])

    building_ids_split = np.array_split(building_ids, number_of_parts)
    building_ids = list(building_ids_split[part])
    N = len(building_ids)

    # if len(sys.argv) < 2:
    #     N = 1
    # else:
    #     N = int(sys.argv[1])
    # building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run jacobi iterations for each floor plan
    MAX_ITER = 10_000
    ABS_TOL = 1e-4

    all_u = np.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
        all_u[i] = u

    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))