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