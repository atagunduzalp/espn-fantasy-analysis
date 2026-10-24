import pandas as pd

from config import get_season
from utils import percentage_calculation


def get_player_snapshot(player):
    """Return the player's current-season last-15-day averages, or {} if unavailable."""
    stats_map = getattr(player, "stats", None) or {}
    last_15 = stats_map.get(f"{get_season()}_last_15") or {}
    avg = last_15.get("avg")
    if not isinstance(avg, dict) or not avg:
        return {}

    snapshot = avg.copy()
    percentage_calculation(snapshot)
    return snapshot


def recommend_players(league, close_categories, pool_size=50):
    """Return all eligible free agents ranked by how much they help in the close categories.

    The UI handles pagination, so the full sorted list is returned.
    """
    if not close_categories:
        return pd.DataFrame()

    free_agents = league.free_agents(size=pool_size)
    free_agents = [player for player in free_agents if not getattr(player, "injured", False)]

    data = []
    for player in free_agents:
        player_stats = get_player_snapshot(player)
        if not player_stats:
            continue

        row = {
            "Name": player.name,
            "Position": player.position,
            "Team": getattr(player, "proTeam", "")
        }

        for cat in close_categories:
            row[cat] = player_stats.get(cat, 0)

        data.append(row)

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["Score"] = 0.0

    for cat in close_categories:
        if cat not in df.columns:
            continue

        max_val = df[cat].max()
        if max_val == 0:
            continue

        if cat == "TO":
            df[f"{cat}_score"] = 1 - (df[cat] / max_val)
        else:
            df[f"{cat}_score"] = df[cat] / max_val

        df["Score"] += df[f"{cat}_score"]

    df = df.sort_values(by="Score", ascending=False)
    cols = ["Name", "Position", "Team"] + close_categories + ["Score"]
    return df[cols].reset_index(drop=True)
