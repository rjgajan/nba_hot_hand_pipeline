import numpy as np
import statistics
from typing import Iterable, Dict

def count_hot_streaks(
    ppm_list: Iterable[float],
    threshold: float,
    window: int = 3
) -> int:
    """Count contiguous sub‐sequences of length `window` whose mean ≥ threshold."""
    arr = list(ppm_list)
    count = 0
    for i in range(len(arr) - window + 1):
        if np.mean(arr[i : i + window]) >= threshold:
            count += 1
    return count

def run_mc(
    ppm_list: Iterable[float],
    nsim: int,
    threshold: float = None,
    window: int = 3
) -> Dict[str, float]:
    """
    Run bootstrap & classic Monte Carlo on ppm_list.
    - If threshold is None, set = 80th percentile of ppm_list.
    - Returns dict with historical, bootstrap_mean/std, classic_mean/std, threshold, window.
    """
    data = list(ppm_list)
    n = len(data)

    # 1) threshold
    if threshold is None:
        threshold = float(np.percentile(data, 80))

    # 2) historical
    hist = count_hot_streaks(data, threshold, window)

    # 3) bootstrap
    bs = np.empty(nsim, dtype=int)
    for i in range(nsim):
        sim = np.random.choice(data, size=n, replace=True)
        bs[i] = count_hot_streaks(sim, threshold, window)
    bs_mean = float(bs.mean())
    bs_std  = float(bs.std(ddof=1))

    # 4) classic
    mu = statistics.mean(data)
    sigma = statistics.stdev(data)
    cl = np.empty(nsim, dtype=int)
    for i in range(nsim):
        sim = np.random.normal(mu, sigma, size=n)
        cl[i] = count_hot_streaks(sim, threshold, window)
    cl_mean = float(cl.mean())
    cl_std  = float(cl.std(ddof=1))

    # 5) return
    return {
        'historical':      hist,
        'bootstrap_mean':  bs_mean,
        'bootstrap_std':   bs_std,
        'classic_mean':    cl_mean,
        'classic_std':     cl_std,
        'threshold':       threshold,
        'window':          window
    }