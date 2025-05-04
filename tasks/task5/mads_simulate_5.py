from os.path import join
import sys
import matplotlib.pyplot as plt
from time import time
from scipy.optimize import curve_fit

import numpy as np

from multiprocessing.pool import Pool
n_proc_list = [1, 2, 3, 4, 5, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)

    for i in range(max_iter):
        # Compute average of left, right, up and down neighbors, see eq. (1)
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break
    return u


def jacobi_multiple(u0_list, interior_mask_list, max_iter, atol=1e-6):
    res = []
    for u0, interior_mask in zip(u0_list, interior_mask_list):
        u = jacobi(u0, interior_mask, max_iter, atol)
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

def exp_saturating(x, L, k, x0):
    return L * (1 - np.exp(-k * (x - x0)))

def plot_speedup(n_proc, time_1, times):
    speed_ups = []
    for time in times:
        speed_ups.append(time_1 / time)
    speedup = np.array(speed_ups)
    
    # Plot the measured speedup
    plt.plot(n_proc, speedup, 'o', label='Measured Speedup')

    # Fit the saturating exponential curve
    p0 = [max(speedup), 0.1, 0]  # Initial guess: [L, k, x0]
    bounds = ([0, 0, -np.inf], [np.inf, np.inf, np.inf])  # Ensure k > 0
    popt, _ = curve_fit(exp_saturating, n_proc, speedup, p0=p0, bounds=bounds, maxfev=10000)
    
    # Predict using the fitted function
    n_proc_fit = np.linspace(min(n_proc), max(n_proc), 200)
    speedup_fit = exp_saturating(n_proc_fit, *popt)
    
    # Plot the fit
    plt.plot(n_proc_fit, speedup_fit, 'r--', label=f'Exponential Fit')
    
    plt.xticks(n_proc)
    plt.xlabel('Number of processes')
    plt.ylabel('Speedup')
    plt.title('Speedup of wall heat simulation script')
    plt.grid()
    plt.legend()
    plt.savefig('/zhome/09/8/169747/02613/mini_project/task5/speedup.png')
    plt.close()


if __name__ == '__main__':
    time_1 = None  # Initialize time_1 to None
    times = []  # List to store wall times for each n_proc

    for n_proc in n_proc_list:
        start_time = time()  # Start timing

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
        # for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        #     u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
        #     all_u[i] = u

        # Split data in the first coordinate
        all_u0_split = np.array_split(all_u0, n_proc)
        all_interior_mask_split = np.array_split(all_interior_mask, n_proc)

        # Parallel processing
        with Pool(n_proc) as pool:
            results_async = [
                pool.apply_async(jacobi_multiple, (all_u0_split[i], all_interior_mask_split[i], MAX_ITER, ABS_TOL))
                for i in range(n_proc)
            ]
            results_split = [r.get() for r in results_async]

        # Combine results
        results = [x for res in results_split for x in res]
        all_u = np.array(results)
        
        # Print summary statistics in CSV format
        stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
        print('building_id, ' + ', '.join(stat_keys))  # CSV header
        for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
            stats = summary_stats(u, interior_mask)
            print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))

        wall_time = time() - start_time
        times.append(wall_time)

        if n_proc == 1:
            time_1 = wall_time

    print(times)

    # Plot speedup
    plot_speedup(n_proc_list, time_1, np.array(times))