from os.path import join
import sys
import numpy as np
from numba import cuda

@cuda.jit
def _jacobi_kernel(u, u_new, mask):
    j, i = cuda.grid(2)  # j = col, i = row

    if 0 < i < u.shape[0] - 1 and 0 < j < u.shape[1] - 1:
        avg = 0.25 * (u[i, j - 1] + u[i, j + 1] + u[i - 1, j] + u[i + 1, j])

        # TODO: Slides be like: "avoid branching". Me: yOU cAn't tElL mE wHaT tO dO
        # If anyone feels fresh to refactor this to avoid the branching, please do so :))
        if mask[i, j]:
            u_new[i, j] = avg
        else:
            u_new[i, j] = u[i, j]

# Cursed unused input _ to match the signature of the other jacobi functions, deal with it :)
def jacobi(u, interior_mask, num_iter, _): 
    u_cutted = np.copy(u[1:-1, 1:-1]) # Cut off the boundary
    d_u = cuda.to_device(u_cutted)
    d_u_new = cuda.device_array_like(u_cutted)
    d_mask = cuda.to_device(interior_mask)

    tpb = (32, 32)
    bpg = ((u_cutted.shape[1] + tpb[1] - 1) // tpb[1],
           (u_cutted.shape[0] + tpb[0] - 1) // tpb[0])

    for _ in range(num_iter):
        _jacobi_kernel[bpg, tpb](d_u, d_u_new, d_mask)
        d_u, d_u_new = d_u_new, d_u  

    return np.pad(d_u.copy_to_host(), pad_width=1, mode='constant', constant_values=0)



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