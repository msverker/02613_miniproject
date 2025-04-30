import numpy as np
from numba import cuda


@cuda.jit
def jacobi_kernel(u, u_new, mask):
    i = cuda.grid(1)  # j = col, i = row

    if i < mask.shape[0]:
        i_mask, j_mask = mask[i]
        u_new[i_mask, j_mask] = 0.25 * (u[i_mask, j_mask - 1] + u[i_mask, j_mask + 1] + u[i_mask - 1, j_mask] + u[i_mask + 1, j_mask])


def jacobi_cuda(u, interior_mask, num_iter):
    u_cutted = np.copy(u[1:-1, 1:-1]) # Cut off the boundary
    mask_idxs = np.stack(np.where(interior_mask), axis=-1).astype(np.int32)
    print(mask_idxs)
    d_u = cuda.to_device(u_cutted)
    d_u_new = cuda.to_device(u_cutted)
    d_mask_idx = cuda.to_device(mask_idxs)
    
    tpb = 256
    bpg = (mask_idxs.shape[0] + tpb - 1) // tpb
    start = time.time()
    for i in range(num_iter):
        jacobi_kernel[bpg, tpb](d_u, d_u_new, d_mask_idx)
        d_u, d_u_new = d_u_new, d_u  
    end = start - time.time()
    print(f"Time taken: {end:.2f} seconds")

    return np.pad(d_u.copy_to_host(), pad_width=1, mode='constant', constant_values=0)