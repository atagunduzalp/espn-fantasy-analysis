
import streamlit as st
import weekly_analysis
from datetime import date as dt_date
from team_radar_streamlit import team_radar_page

# Başlık
st.title("Fantasy NBA Analysis App")

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
    st.session_state.match_date = date.today()

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
            do_the_ops()

def do_the_ops():
    if st.session_state.teams_submitted:
        st.write("League ID:", st.session_state.league_id)
        st.write("Your Team:", st.session_state.team_name)
        st.write("Opponent Team:", st.session_state.opponent_team_name)
        st.write("Match Date:", st.session_state.match_date)
        league = weekly_analysis.get_league_info(st.session_state.league_id)
        weekly_analysis.get_teams_stats(st.session_state.get('team_name'), st.session_state.match_date, league,
                                        st.session_state.league_stats_selection)
        weekly_analysis.get_teams_stats(st.session_state.get('opponent_team_name'), st.session_state.match_date, league,
                                        st.session_state.league_stats_selection)

if st.button("Reset"):
    reset()
    # st.experimental_rerun()

if __name__ == '__main__':
    # Sidebar Menü
    st.sidebar.title("🏀 ESPN Fantasy Tools")
    page = st.sidebar.radio(
        "Mod Seç:",
        ["Weekly Analysis", "Team Radar Chart"]
    )

    if page == "Team Radar Chart":
        team_radar_page()
    elif page == "Weekly Analysis":
        get_league_id()
#     get_team_names(st.session_state.league_id)