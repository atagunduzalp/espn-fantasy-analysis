import streamlit as st
import pandas as pd
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from espn_api.basketball import League

def team_radar_page():
    st.markdown('<div class="page-title">🕸️ Team Radar</div>', unsafe_allow_html=True)
    # st.title("🕸️ Team Matchup Radar")

    # --- Girdiler ---
    LEAGUE_ID = st.text_input("League ID", placeholder="ex: 123456789")

    if not (LEAGUE_ID):
        st.info("Lütfen yukarıdaki bilgileri doldurun.")
        return

    try:
        league = League(league_id=int(LEAGUE_ID), year=2026, debug=False)
        st.success(f"Lig başarıyla yüklendi: {league.settings.name}")
    except Exception as e:
        st.error(f"Lig bilgisi alınamadı: {e}")
        return

    # --- Takım seçimi ---
    teams = [t.team_name for t in league.teams]
    my_team_name = st.selectbox("Takımını Seç", teams)
    my_team = next(t for t in league.teams if t.team_name == my_team_name)

    # --- Hafta seçimi ---
    scoreboard = league.scoreboard()
    week_labels = [f"Week {i+1}" for i in range(len(scoreboard))]
    selected_week_idx = st.selectbox("Hafta Seç", range(len(scoreboard)), format_func=lambda i: week_labels[i])

    matchup = league.scoreboard()[selected_week_idx]
    opp_team = matchup.away_team if matchup.home_team.team_id == my_team.team_id else matchup.home_team

    opp_names = [t.team_name for t in league.teams]
    opp_team_name = st.selectbox("Rakip Takım Seç", opp_names, index=opp_names.index(opp_team.team_name))
    opp_team = next(t for t in league.teams if t.team_name == opp_team_name)

    # --- Profil fonksiyonu ---
    def get_team_profile(team, stat_key='2026_last_15'):
        data = []
        for p in team.roster:
            stats = p.stats.get(stat_key, {}) or {}
            avg = stats['avg'] if isinstance(stats, dict) and 'avg' in stats else stats
            data.append({
                "player": p.name,
                "PTS": avg.get("PTS", 0),
                "REB": avg.get("REB", 0),
                "AST": avg.get("AST", 0),
                "STL": avg.get("STL", 0),
                "BLK": avg.get("BLK", 0),
                "3PM": avg.get("3PM", 0),
                "FG%": avg.get("FG%", 0),
                "FT%": avg.get("FT%", 0),
                "TO": avg.get("TO", 0)
            })
        df = pd.DataFrame(data)
        cats = ["PTS","REB","AST","STL","BLK","3PM","FG%","FT%","TO"]
        df[cats] = df[cats].apply(pd.to_numeric, errors="coerce").fillna(0)
        df["TO"] = -df["TO"]
        df["total"] = df[["PTS","REB","AST","STL","BLK","3PM"]].sum(axis=1)
        df = df[df["total"] > 0]
        return df[cats].mean()

    # --- Radar çizimi ---
    def compare_team_radars(team1_profile, team2_profile, labels):
        cats = list(team1_profile.index)
        N = len(cats)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(6,6))
        plt.xticks(angles[:-1], cats, color='grey', size=9)
        ax.set_rlabel_position(0)
        plt.yticks([-2,-1,0,1,2], ["-2","-1","0","1","2"], color="grey", size=7)
        plt.ylim(-2.5,2.5)
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)

        colors = ["#F27A21", "#808080"]
        for profile, color, label in zip([team1_profile, team2_profile], colors, labels):
            values = profile.tolist() + [profile.tolist()[0]]
            ax.plot(angles, values, linewidth=2, label=label, color=color)
            ax.fill(angles, values, alpha=0.15, color=color)

        plt.legend(bbox_to_anchor=(1.25,1.05))
        plt.title("Head-to-Head 9-Cat Matchup Radar", size=13, y=1.08)
        st.pyplot(fig)

    # --- Buton ---
    if st.button("Radar Grafiğini Oluştur"):
        my_profile = get_team_profile(my_team)
        opp_profile = get_team_profile(opp_team)
        profiles = pd.DataFrame([my_profile, opp_profile])
        for c in profiles.columns:
            if profiles[c].std() != 0:
                profiles[c] = (profiles[c] - profiles[c].mean()) / profiles[c].std()
        compare_team_radars(profiles.iloc[0], profiles.iloc[1], labels=(my_team.team_name, opp_team.team_name))
