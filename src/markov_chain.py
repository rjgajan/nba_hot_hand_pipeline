import pandas as pd
from typing import Sequence

def build_markov(ppm_series: Sequence[float]) -> pd.DataFrame:
    """
    1.) Build a 3 by 3 Markov chain from ppm_series via 20/60/20 discretization.
    2.) 'hot' = top 20%
    3.) 'typical' = middle 60%
    4.) 'cold' = bottom 20%
    5.) Return as df.
    """
    arr = pd.Series(ppm_series).reset_index(drop=True)

    # Compute 20th and 80th percentiles
    low_thresh, high_thresh = arr.quantile([0.20, 0.80])

    # Assign labels
    def label(x):
        if x >= high_thresh:
            return 'hot'
        elif x <= low_thresh:
            return 'cold'
        else:
            return 'typical'

    states = arr.map(label)

    # Build transition probabilities
    prev = states.shift(1).fillna(states.iloc[0])
    tm = pd.crosstab(prev, states, normalize='index')

    # Ensure consistent state order and fill missing
    order = ['hot', 'typical', 'cold']
    tm = tm.reindex(index=order, columns=order, fill_value=0.0)

    tm.index.name = 'from_state'
    tm.columns.name = 'to_state'
    return tm