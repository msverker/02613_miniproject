import numpy as np
from numba import jit


@jit(nopython=True)
def jacobi(u, interior_mask, max_iter, atol=1e-6):
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