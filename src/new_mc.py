import numpy as np
import statistics
from typing import Iterable, Dict

def count_hot_streaks(
    ppm_list: Iterable[float],
    threshold: float,
    window: int = 3
) -> int:
    """Count contiguous sub‑sequences of length 'window' whose mean ≥ threshold."""
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
    Run bootstrap & classic Monte Carlo simulation on ppm_list.
    
    threshold: if None, set to the 80th percentile (top 20%) of ppm_list.
    window:    length of streak to consider "hot".
    
    Prints a summary report like:
    
      Hot‑Streak Analysis (window=3, threshold=25.40 PPM)
    
       Historical streaks: 12
       Bootstrap   mean: 10.23, std: 2.11
       Classic     mean:  9.87, std: 3.45
    
    Returns a dict with keys:
      'historical', 'bootstrap_mean', 'bootstrap_std',
      'classic_mean', 'classic_std', 'threshold', 'window'
    """
    data = list(ppm_list)
    n_games = len(data)

    # 1) Determine threshold
    if threshold is None:
        threshold = float(np.percentile(data, 80))

    # 2) Historical count
    hist = count_hot_streaks(data, threshold, window)

    # 3) Bootstrap simulation
    bs = np.empty(nsim, dtype=int)
    for i in range(nsim):
        sim = np.random.choice(data, size=n_games, replace=True)
        bs[i] = count_hot_streaks(sim, threshold, window)
    bs_mean = float(bs.mean())
    bs_std  = float(bs.std(ddof=1))

    # 4) Classic (Gaussian) simulation
    mu = statistics.mean(data)
    sigma = statistics.stdev(data)
    cl = np.empty(nsim, dtype=int)
    for i in range(nsim):
        sim = np.random.normal(mu, sigma, size=n_games)
        cl[i] = count_hot_streaks(sim, threshold, window)
    cl_mean = float(cl.mean())
    cl_std  = float(cl.std(ddof=1))

    # 5) Print the report
    report = (
        f"Hot‑Streak Analysis (window={window}, threshold={threshold:.2f} PPM)\n\n"
        f" Historical streaks: {hist}\n"
        f" Bootstrap   mean: {bs_mean:.2f}, std: {bs_std:.2f}\n"
        f" Classic     mean: {cl_mean:.2f}, std: {cl_std:.2f}\n"
    )
    print(report)

    # 6) Return raw numbers if caller needs them
    return {
        'historical':      hist,
        'bootstrap_mean':  bs_mean,
        'bootstrap_std':   bs_std,
        'classic_mean':    cl_mean,
        'classic_std':     cl_std,
        'threshold':       threshold,
        'window':          window
    }