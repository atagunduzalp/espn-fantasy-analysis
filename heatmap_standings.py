import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from espn_api.basketball import League

# ---- LEAGUE INFO ----
# LEAGUE_ID = st.text_input("League ID", placeholder="ex: 123456789")
# league = League(league_id='170805702', year=2026, debug=False)
def heatmap_page():
    st.markdown('<div class="page-title">🔥 Category Heatmap</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        .main > div {
            max-width: 95%;
            padding-left: 5%;
            padding-right: 5%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # st.title("Heatmap Standing Analysis Page")

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

    # ---- COLLECT TEAM CATEGORY TOTALS ----
    data = []
    for team in league.teams:
        stats = {
            "Team": team.team_name,
            "PTS": team.stats.get("PTS", 0),
            "REB": team.stats.get("REB", 0),
            "AST": team.stats.get("AST", 0),
            "STL": team.stats.get("STL", 0),
            "BLK": team.stats.get("BLK", 0),
            "3PM": team.stats.get("3PM", 0),
            "FG%": team.stats.get("FG%", 0),
            "FT%": team.stats.get("FT%", 0),
            "TO": team.stats.get("TO", 0),
            "Standing": team.standing
        }
        data.append(stats)

    df = pd.DataFrame(data)
    df = df.sort_values("Standing", ascending=True)
    df.set_index("Team", inplace=True)

    df["TO_adj"] = -df["TO"]
    df = df.drop(columns=["TO", "Standing"])
    df_norm = df.copy()

    for col in df_norm.columns:
        if col != "Category Points":
            df_norm[col] = (df_norm[col] - df_norm[col].min()) / (df_norm[col].max() - df_norm[col].min())

    # ---- HEATMAP ----
    fig, ax = plt.subplots(figsize=(12, 8))
    # plt.figure(figsize=(12,6))
    ax = sns.heatmap(
        cmap="RdYlGn",
        annot=df,
        linewidths=.5,
        fmt=".2f",
        data = df_norm,
        cbar=False
    )
    ax.xaxis.tick_top()  # <-- kolon isimlerini yukarı al
    ax.xaxis.set_label_position('top')
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=9)

    plt.title("Fantasy League Category Strength Heatmap")
    # plt.show()
    st.pyplot(fig)

