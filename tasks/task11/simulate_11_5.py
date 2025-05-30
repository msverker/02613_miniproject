# We parallelize as in simulate_5.py using the jit version

import sys

import numpy as np
from numba import jit
from os.path import join
from multiprocessing.pool import Pool

n_proc = int(sys.argv[2])


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


# @jit(nopython=True)
# def jacobi_jit(u, interior_mask, max_iter, atol=1e-6):
#     u = np.copy(u)
    
#     for i in range(max_iter):
#         # Compute average of left, right, up and down neighbors, see eq. (1)
#         u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
#         u_new_interior = np.where(interior_mask, u_new, u[1:-1, 1:-1])
#         delta = np.abs(u[1:-1, 1:-1] - u_new_interior).max()
#         u[1:-1, 1:-1] = u_new_interior
        
#         if delta < atol:
#             break
    
#     return u

@jit(nopython=True)
def jacobi_jit_for_loop(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    
    n, m = u.shape
    u_new = np.copy(u)
    
    n_interior, m_interior = interior_mask.shape
    interior_mask_list = []
    for i in range(n_interior):
        for j in range(m_interior):
            if interior_mask[i, j]:
                interior_mask_list.append((i, j))
    
    u_new_interior = np.copy(u[1:-1, 1:-1])
    for _ in range(max_iter):
        for i in range(1, n - 1):
            for j in range(1, m - 1):
                u_new[i, j] = 0.25 * (u[i, j-1] + u[i, j+1] + u[i-1, j] + u[i+1, j])

        u_new_small = u_new[1:-1, 1:-1] 
        for (i, j) in interior_mask_list:
            new_value = u_new_small[i, j]
            u_new_interior[i, j] = new_value

        delta = 0
        for i in range(n - 2):
            for j in range(m - 2):
                if delta < abs(u[1:-1, 1:-1][i, j] - u_new_interior[i, j]):
                    delta = abs(u[1:-1, 1:-1][i, j] - u_new_interior[i, j])
        
        u[1:-1, 1:-1] = u_new_interior
        
        if delta < atol:
            break
    
    return u


def jacobi_multiple(u0_list, interior_mask_list, max_iter, atol=1e-6):
    res = []
    for u0, interior_mask in zip(u0_list, interior_mask_list):
        u = jacobi_jit_for_loop(u0, interior_mask, max_iter, atol)
        res.append(u)

    return res


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

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    all_u = np.empty_like(all_u0)
    all_u0_split = np.array_split(all_u0, n_proc)
    all_interior_mask_split = np.array_split(all_interior_mask, n_proc)
    
    pool = Pool(n_proc)
    results_async = [
        pool.apply_async(jacobi_multiple, (all_u0_split[i], all_interior_mask_split[i], MAX_ITER, ABS_TOL, ))
        for i in range(n_proc)
    ]
    results_split = [r.get() for r in results_async]
    results = [x for res in results_split for x in res]
    all_u = np.array(results)

    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
