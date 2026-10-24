import os

import pandas as pd

from config import get_season
from waiver_analysis import get_player_snapshot, recommend_players


class FakePlayer:
    def __init__(self, name, position, pro_team, stats, injured=False):
        self.name = name
        self.position = position
        self.proTeam = pro_team
        self.stats = stats
        self.injured = injured


class FakeLeague:
    def __init__(self, players):
        self._players = players

    def free_agents(self, size=200):
        return self._players[:size]


def test_get_season_uses_env_override(monkeypatch):
    monkeypatch.setenv("ESPN_FANTASY_SEASON", "2028")
    assert get_season() == 2028


def test_snapshot_uses_current_season_last_15_avg():
    season = get_season()
    player = FakePlayer("Alpha", "PF", "LAL", {
        f"{season}_projected": {"avg": {"PTS": 22.0}},
        f"{season}_last_15": {"avg": {"PTS": 25.0}, "total": {"PTS": 250.0}},
    })

    assert get_player_snapshot(player)["PTS"] == 25.0


def test_snapshot_ignores_other_windows_and_seasons():
    season = get_season()
    player = FakePlayer("Beta", "PG", "BOS", {
        f"{season}_projected": {"avg": {"PTS": 14.0}},
        f"{season}_last_30": {"avg": {"PTS": 15.0}},
        f"{season - 1}_last_15": {"avg": {"PTS": 30.0}},
    })

    assert get_player_snapshot(player) == {}


def test_snapshot_does_not_use_totals_when_avg_missing():
    player = FakePlayer("Gamma", "SF", "NYK", {
        f"{get_season()}_last_15": {"avg": None, "total": {"PTS": 412.0}},
    })

    assert get_player_snapshot(player) == {}


def test_recommend_players_skips_players_without_last_15():
    season = get_season()
    league = FakeLeague([
        FakePlayer("Alpha", "PF", "LAL", {f"{season}_last_15": {"avg": {"PTS": 25.0, "REB": 10.0, "TO": 3.0}}}),
        FakePlayer("Beta", "PG", "BOS", {f"{season}_projected": {"avg": {"PTS": 40.0, "REB": 4.0, "TO": 4.0}}}),
    ])

    recs = recommend_players(league, ["PTS", "REB", "TO"])

    assert isinstance(recs, pd.DataFrame)
    assert list(recs["Name"]) == ["Alpha"]
    assert "Score" in recs.columns


def test_recommend_players_returns_full_sorted_list_for_pagination():
    season = get_season()
    league = FakeLeague([
        FakePlayer(f"P{i}", "C", "DEN", {f"{season}_last_15": {"avg": {"PTS": float(i)}}})
        for i in range(1, 36)
    ])

    recs = recommend_players(league, ["PTS"])

    assert len(recs) == 35
    assert recs.iloc[0]["Name"] == "P35"
    assert recs["Score"].is_monotonic_decreasing
