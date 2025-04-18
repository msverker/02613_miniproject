import numpy as np
from numba import jit


"""Alternative implementation largely still using numpy, slower than for loops"""


@jit(nopython=True)
def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    for i in range(max_iter):
        # Compute average of left, right, up and down neighbors, see eq. (1)
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = np.where(interior_mask, u_new, u[1:-1, 1:-1])
        delta = np.abs(u[1:-1, 1:-1] - u_new_interior).max()
        u[1:-1, 1:-1] = u_new_interior
        if delta < atol:
            break
    return u

