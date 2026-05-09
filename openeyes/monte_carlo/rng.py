from __future__ import annotations

import numpy as np
from scipy.stats import qmc


class PCG64:
    def __init__(self, seed: int) -> None:
        self._rng = np.random.Generator(np.random.PCG64(seed))

    def random(self, size: int | tuple[int, ...] | None = None) -> np.ndarray:
        return self._rng.random(size)


def sobol_vectors(n: int, dim: int, scramble: bool = False) -> np.ndarray:
    sampler = qmc.Sobol(d=dim, scramble=scramble)
    return sampler.random(n=n)


def box_muller(u1: np.ndarray, u2: np.ndarray) -> np.ndarray:
    u1 = np.clip(u1, 1e-12, 1.0)
    return np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
