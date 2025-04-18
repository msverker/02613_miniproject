from os.path import join
import sys

import numpy as np
from numba import jit, cuda
from multiprocessing.pool import Pool


# ---------------------------------------------------------------------------- #
#                                    Globals                                   #
# ---------------------------------------------------------------------------- #
# Globals I'm too lazy to argparse :3

MAX_ITER = 20_000 # NOTE: Change this to 3601 if you want consistent results for ex. 8 and 7 ;d
ABS_TOL = 1e-4
LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
SIZE = 512

# Only used for multiprocessing exercises
N_PROC_LIST = [1, 2, 3, 4, 5, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]


# ---------------------------------------------------------------------------- #
#                               Default Functions                              #
# ---------------------------------------------------------------------------- #

def load_data(load_dir, bid):
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

# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #


if __name__ == '__main__':
    import time
    import argparse
    
    """
    Jacobi exercise numbers:
        7: NUMBA JIT on CPU
        8: CUDA JIT
        9: Cupy
    
    Multiprocessing exercise numbers:
        5: Multiprocessing with static scheduling
        6: Multiprocessing with dynamic scheduling
    
    Exercise 11 can be run by running with both -j and -mp arguments set to non-default values.
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-N', '--num_buildings', type=int, default=1, help='Number of buildings to simulate')
    parser.add_argument('-j', '--jacobi_exercise', type=int, default=-1, choices=[7,8,9], help='Jacobi implementation exercise number, defaults to the default jacobi function')
    parser.add_argument('-mp', '--multi_process_exercise', type=int, default=-1, choices=[5,6], help='Multiprocessing exercise number, defaults to serial execution')
    
    args = parser.parse_args()
    
    if args.jacobi_exercise == 8 and args.parallel_exercise != -1:
        raise ValueError('Exercise 8 runs with CUDA JIT, it cannot be run with multiprocessing')
    
    N = args.num_buildings
    
    if args.multi_process_exercise == 5:
        from exercise_specific_fn.ex5 import jacobi_multiple 
    
    match args.jacobi_exercise:
        case 7:
            from exercise_specific_fn.ex7 import jacobi
        case 8:
            from exercise_specific_fn.ex8 import jacobi
        case 9:
            from exercise_specific_fn.ex9 import load_data, jacobi
        case -1:
            # Default simulate.py behavior
            pass 
        case _:
            raise NotImplementedError('Invalid exercise number. Must be between 5 and 9.')

    
    # Start the timer - RUN FOREST RUN
    time_start = time.time()
    
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()
        
    building_ids = building_ids[:N]
    
    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    
    if args.multi_process_exercise == -1:
        all_u = np.empty_like(all_u0)
        for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
            u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
            all_u[i] = u
        
        print(f"Serial Jaxobi Ex {args.jacobi_exercise} - time taken: {time.time() - time_start:.2f} seconds")
    else:
        # Run in parallel using multiprocessing
        serial_times = []
        parallel_times = []
        
        serial_time_outside_procs = time.time() - time_start
        for n_proc in N_PROC_LIST:
            proc_serial_time_start = time.time()
            
            pool = Pool(n_proc)
            if args.multi_process_exercise == 5:
                # Manually split the tasks to be the same as the number of processes making static scheduling
                all_u0_split = np.array_split(all_u0, n_proc) 
                all_interior_mask_split = np.array_split(all_interior_mask, n_proc)
                
                parallel_time_start = time.time()
                
                results_async = [
                    pool.apply_async(jacobi_multiple, (all_u0_split[i], all_interior_mask_split[i], MAX_ITER, jacobi, ABS_TOL, ))
                    for i in range(n_proc)
                    ]
            elif args.multi_process_exercise == 6:
                # TODO: Needs debugging, didn't have time to finish this will do soon
                
                # Dynamic scheduling goes brrrrrrrrr
                parallel_time_start = time.time()
                
                results_async = [
                    pool.apply_async(jacobi, (u0, mask, MAX_ITER, ABS_TOL))
                    for u0, mask in zip(all_u0, all_interior_mask)
                ]
            results_split = [r.get() for r in results_async]
            
            parallel_times.append(time.time() - parallel_time_start)
            all_u = np.array([x for res in results_split for x in res])
            
            serial_times.append(time.time() - proc_serial_time_start - parallel_times[-1] + serial_time_outside_procs)
        
        # TODO: Potentially change this to save to a file instead
        print(f"Scheduling tactic {args.multi_process_exercise} - Jacobi tactic {args.jacobi_exercise}:")
        print(f"# of processors: {N_PROC_LIST}")
        print(f"Serial time for process: {serial_times}")
        print(f"Parallel time for process: {parallel_times}")
        print(f"Total time for process: {np.array(parallel_times) + np.array(serial_times)}")
                    
    # Print summary statistics in CSV format (NOTE: For multiprocessing it just prints the last one)
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))

