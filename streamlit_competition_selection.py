
import streamlit as st
import weekly_analysis
from datetime import date as dt_date

# # Başlık
# st.title("Maç Bilgi Girişi")
#
# if "refresh_done" not in st.session_state:
#     st.session_state["refresh_done"] = False
#
# # Kullanıcıdan Lig ID, Takım Adı, Rakip Takım Adı ve Tarih Bilgilerini Alma
# league_id_str = st.text_input("League ID", value=st.session_state.get("league_id_str", ""))
# team_name = st.text_input("Team Name", value=st.session_state.get("team_name", ""))
# opponent_team_name = st.text_input("Opponent Team Name", value=st.session_state.get("opponent_team_name", ""))
# date = st.date_input("Date", value=st.session_state.get("date", dt_date.today()))
#
# # Session'ı sıfırlama butonu
# if st.button("Reset Session") and not st.session_state["refresh_done"]:
#     st.session_state.clear()
#     st.session_state["refresh_done"] = True
#     st.experimental_rerun()
#
# # Gönder butonu
# if st.button("Bilgileri Gönder"):
#     # Session state'i sıfırlamak için flag'i güncelle
#     st.session_state["refresh_done"] = False
#     st.session_state["league_id_str"] = league_id_str
#     st.session_state["team_name"] = team_name
#     st.session_state["opponent_team_name"] = opponent_team_name
#     st.session_state["date"] = date
#
#     # Girilen Lig ID'yi integer'a çevirme
#     try:
#         league_id = int(league_id_str) if league_id_str else None
#     except ValueError:
#         st.error("Lütfen geçerli bir sayı girin.")
#         st.stop()  # Hatalı giriş varsa işlemi durdur
#
#     # weekly_analysis modülünden fonksiyonları çağırma
#     league = weekly_analysis.get_league_info(league_id)
#     weekly_analysis.get_teams_stats(league_id, team_name, date, league)
#     weekly_analysis.get_teams_stats(league_id, opponent_team_name, date, league)


# Başlık
st.title("Match Analysis App")

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

        # team_name = st.selectbox("Select your Team:", team_list, key="team_name")
        # opponent_team_name = st.selectbox("Select Opponent Team:", team_list, key="opponent_team_name")

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

            # result = f"Simulation for {team_name} vs {opponent_team_name} on {match_date} in League {league_id} is complete!"
            # st.success(result)

if st.button("Reset"):
    reset()
    # st.experimental_rerun()

if __name__ == '__main__':
    get_league_id()
#     get_team_names(st.session_state.league_id)