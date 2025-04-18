from typing import Callable

def jacobi_multiple(u0_list, interior_mask_list, max_iter, jacobi_fn: Callable, atol=1e-6):
    res = []
    for u0, interior_mask in zip(u0_list, interior_mask_list):
        u = jacobi_fn(u0, interior_mask, max_iter, atol)
        res.append(u)

    return res
