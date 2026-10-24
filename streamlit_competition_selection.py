
import streamlit as st
import weekly_analysis
import heatmap_standings
from datetime import date as dt_date
from team_radar_streamlit import team_radar_page

# st.markdown("""
# <style>
# /* BUTTONS */
# div.stButton > button {
#     background-color: #F27A21 !important;
#     color: white !important;
#     border-radius: 8px !important;
#     border: none !important;
#     font-weight: 600;
#     padding: 0.6em 1.2em;
# }
# div.stButton > button:hover {
#     background-color: #ff8f3a !important;
# }
#
# /* SELECT DROPDOWNS */
# .stSelectbox label {
#     color: #f27a21 !important;
#     font-weight: 600;
# }
#
# /* HEADERS */
# h1, h2, h3 {
#     color: #F27A21 !important;
#     font-weight: 700 !important;
# }
#
# /* SIDEBAR */
# .css-1d391kg, .css-12oz5g7 {
#     background-color: #111 !important;
# }
# <div style="text-align:center;padding:10px 0;">
#     <span style="font-size:32px;font-weight:800;color:#F27A21;">🏀 Fantasy NBA Analytics</span><br>
#     <span style="font-size:16px;color:#DDD;">Advanced Stats & Matchup Insights</span>
# </div>
# </style>
# """, unsafe_allow_html=True)

st.markdown("""
<style>
.main-title {
    font-size: 28px;
    font-weight: 800;
    color: #F27A21;
    padding-bottom: 0px;
}
.sub-header {
    font-size: 14px;
    color: #BBBBBB;
    margin-bottom: 20px;
}
.page-title {
    font-size: 24px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏀 Fantasy NBA Tools</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced Matchup Analytics</div>', unsafe_allow_html=True)


# Başlık
# st.title("Fantasy NBA Analysis App")

# Session State ile durum yönetimi
if "league_id" not in st.session_state:
    st.session_state.league_id = ""
if "league_id_submitted" not in st.session_state:
    st.session_state.league_id_submitted = False
if "teams_submitted" not in st.session_state:
    st.session_state.teams_submitted = False
if "team_name" not in st.session_state:
    st.session_state.team_name = ""
if "opponent_team_name" not in st.session_state:
    st.session_state.opponent_team_name = ""
if "league_stats_selection" not in st.session_state:
    st.session_state.league_stats_selection = ""
if "match_date" not in st.session_state:
    st.session_state.match_date = dt_date.today()

# Reset fonksiyonu
def reset():
    st.session_state.league_id = ""
    st.session_state.league_id_submitted = False
    st.session_state.teams_submitted = False
    st.session_state.team_name = ""
    st.session_state.opponent_team_name = ""
    st.session_state.league_stats_selection = ""
    st.session_state.match_date = dt_date.today()
    st.session_state.owner_unlocked = False

# 1. League ID bilgisi al ve submit butonu

def get_league_id():
    league_id = st.text_input("Enter League ID:", value=st.session_state.league_id)
    if st.button("Submit League ID"):
        if league_id:
            try:
                league_id = int(league_id) if league_id else None
            except ValueError:
                st.error("Lütfen geçerli bir sayı girin.")
                st.stop()  # Hatalı giriş varsa işlemi durdur
            st.session_state.league_id = league_id
            st.session_state.league_id_submitted = True
            st.success(f"League ID '{league_id}' submitted successfully! Now wait for team list.")
        else:
            st.error("Please enter a valid League ID!")
    get_team_names(league_id)


def prepare_date():
    global date
    # Varsayılan olarak bugünün tarihini al
    return st.date_input("Date", value=st.session_state.get("date", dt_date.today()))


#------

def get_team_names(league_id_int):

    # Örnek takım listeleri
    if st.session_state.league_id_submitted:
        team_list = weekly_analysis.get_teams_in_league(league_id_int)

        st.session_state.team_name = st.selectbox(
            "Select your Team:",
            team_list,
            key="team_name_selector"  # Benzersiz key
        )
        st.session_state.opponent_team_name = st.selectbox(
            "Select Opponent Team:",
            team_list,
            key="opponent_team_selector"  # Benzersiz key
        )

        try:
            owner_teams = st.secrets.get("OWNER_TEAMS", [])
        except (FileNotFoundError, AttributeError, KeyError):
            owner_teams = []

        if isinstance(owner_teams, str):
            owner_teams = [owner_teams]
        elif not isinstance(owner_teams, (list, tuple, set)):
            owner_teams = [owner_teams] if owner_teams else []

        if "owner_unlocked" not in st.session_state:
            st.session_state.owner_unlocked = False

        selected_team = st.session_state.team_name
        opp_team = st.session_state.opponent_team_name

        # Eğer seçilen takım seninse ve henüz unlock edilmemişse
        if owner_teams and (selected_team in owner_teams or opp_team in owner_teams) and not st.session_state.owner_unlocked:
            try:
                owner_pass = st.secrets.get("OWNER_PASS")
            except (FileNotFoundError, AttributeError, KeyError):
                owner_pass = None

            if owner_pass is None:
                st.session_state.owner_unlocked = True
                st.warning("⚠️ No OWNER_PASS configured; private-team gate skipped.")
            else:
                password = st.text_input("🔐 Private team. Enter owner key:", type="password")

                if password:
                    if password == owner_pass:
                        st.session_state.owner_unlocked = True
                        st.success("✅ Access granted!")
                    else:
                        st.error("❌ Wrong key — access denied")
                        st.stop()
                else:
                    st.stop()

        st.session_state.league_stats_selection = st.selectbox(
            "Select League stats:",
            ['9-Cat', '9-Cat + 3%'],
            key="league_stat_selection"
        )

        # İşlem butonu
        # Kullanıcıya takım seçimi yaptır
        st.session_state.match_date = prepare_date()
        if st.button("Submit Match Details"):
            st.session_state.teams_submitted = True
        
        if st.session_state.teams_submitted:
            do_the_ops()

def do_the_ops():
    if st.session_state.teams_submitted:
        st.write("League ID:", st.session_state.league_id)
        st.write("Your Team:", st.session_state.team_name)
        st.write("Opponent Team:", st.session_state.opponent_team_name)
        st.write("Match Date:", st.session_state.match_date)
        league = weekly_analysis.get_league_info(st.session_state.league_id)

        df_1 = weekly_analysis.get_teams_stats(st.session_state.get('team_name'), st.session_state.match_date, league,
                                        st.session_state.league_stats_selection)
        df_2 = weekly_analysis.get_teams_stats(st.session_state.get('opponent_team_name'), st.session_state.match_date, league,
                                        st.session_state.league_stats_selection)

        weekly_analysis.color_table(df_1,df_2)

if __name__ == '__main__':
    # Sidebar Menü
    st.sidebar.title("🏀 ESPN Fantasy Tools")
    page = st.sidebar.radio(
        "Select:",
        ["Weekly Analysis", "Team Radar Chart", "Heatmap Standing Analysis"]
    )

    if page == "Team Radar Chart":
        team_radar_page()
    elif page == "Weekly Analysis":
        st.markdown('<div class="page-title">📊 Weekly Matchup Analysis</div>', unsafe_allow_html=True)
        if st.sidebar.button("🔄 Reset Weekly Selection"):
            reset()
        get_league_id()
    elif page == "Heatmap Standing Analysis":
        heatmap_standings.heatmap_page()