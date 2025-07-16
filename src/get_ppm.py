from nba_api.stats.endpoints import PlayerGameLog as pgl
import pandas as pd
import matplotlib.pyplot as plt
import re

_SEASON_RE = re.compile(r'^\d{4}-\d{2}$')

def points_per_min(p_id: str, season_list: list[str]) -> list[float]:
    """Create list of points per minute for each regular season game.
    Expects season_list entries in XXXX-XX format."""

    if not isinstance(season_list, list):
        raise TypeError(f"season_list must be a list of strings, got {type(season_list).__name__}")
    if not season_list:
        raise ValueError("season_list must contain at least one season string")

    for s in season_list:
        if not isinstance(s, str) or not _SEASON_RE.match(s):
            raise ValueError(f"Invalid season format {s!r}: must be 'YYYY-YY' (e.g. '2019-20')")

    ppm_list = []
    for season in season_list:
        try:
            df = pgl(player_id=p_id, season=season).get_data_frames()[0]
        except KeyError:
            raise RuntimeError(f"No data returned for season {season!r}")
        df = df[df['MIN'] > 0].copy()
        df['PPM'] = df['PTS'] / df['MIN']
        ppm_list.append(df['PPM'])

    if not ppm_list:
        raise RuntimeError("No valid data retrieved for any season")

    all_ppm = pd.concat(ppm_list, ignore_index=True)
    return all_ppm.round(3).tolist()

def visualize_distribution(p_id: str, season_list: list[str]):
    ppm = points_per_min(p_id, season_list)
    data = ppm
    plt.figure()
    plt.hist(data, bins=30, edgecolor='black', alpha=0.7, density=False)
    plt.title(f"{data}")
    plt.xlabel("ppm")
    plt.ylabel("count")
    plt.show

if __name__ == "__main__":
    p_id = "2544"
    season_list = ["2016-17","2017-18","2018-19","2019-20"]
    visualize_distribution(p_id, season_list)