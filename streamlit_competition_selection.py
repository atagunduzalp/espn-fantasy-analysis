#
# import streamlit as st
# import weekly_analysis
# from datetime import date
#
# # Başlık
# st.title("Maç Bilgi Girişi")
#
# # Kullanıcıdan Lig ID, Takım Adı, Rakip Takım Adı ve Tarih Bilgilerini Alma
# league_id_str = st.text_input("League ID")
# team_name = st.text_input("Team Name")
# opponent_team_name = st.text_input("Opponent Team Name")
# date = st.date_input("Date", value=date.today())
#
# # Kullanıcı Bilgilerini Göster
# if st.button("Bilgileri Gönder"):
#     league_id = 0
#     print(league_id_str, team_name, opponent_team_name, date)
#
#     try:
#         league_id = int(league_id_str) if league_id_str else None
#     except ValueError:
#         st.error("Lütfen geçerli bir sayı girin.")
#
#     weekly_analysis.get_teams_stats(league_id, team_name, date)
#     weekly_analysis.get_teams_stats(league_id, opponent_team_name, date)
#


import streamlit as st
import weekly_analysis
from datetime import date as dt_date

# Başlık
st.title("Maç Bilgi Girişi")

# Gerekli session state değişkenlerini kontrol ediyoruz
if "refresh_done" not in st.session_state:
    st.session_state["refresh_done"] = False

# Kullanıcıdan Lig ID, Takım Adı, Rakip Takım Adı ve Tarih Bilgilerini Alma
league_id_str = st.text_input("League ID", value=st.session_state.get("league_id_str", ""))
team_name = st.text_input("Team Name", value=st.session_state.get("team_name", ""))
opponent_team_name = st.text_input("Opponent Team Name", value=st.session_state.get("opponent_team_name", ""))
date = st.date_input("Date", value=st.session_state.get("date", dt_date.today()))

# Session'ı sıfırlama butonu
if st.button("Reset Session") and not st.session_state["refresh_done"]:
    st.session_state.clear()
    st.session_state["refresh_done"] = True
    st.experimental_rerun()

# Gönder butonu
if st.button("Bilgileri Gönder"):
    # Session state'i sıfırlamak için flag'i güncelle
    st.session_state["refresh_done"] = False
    st.session_state["league_id_str"] = league_id_str
    st.session_state["team_name"] = team_name
    st.session_state["opponent_team_name"] = opponent_team_name
    st.session_state["date"] = date

    # Girilen Lig ID'yi integer'a çevirme
    try:
        league_id = int(league_id_str) if league_id_str else None
    except ValueError:
        st.error("Lütfen geçerli bir sayı girin.")
        st.stop()  # Hatalı giriş varsa işlemi durdur

    # weekly_analysis modülünden fonksiyonları çağırma
    league = weekly_analysis.get_league_info(league_id)
    weekly_analysis.get_teams_stats(league_id, team_name, date, league)
    weekly_analysis.get_teams_stats(league_id, opponent_team_name, date, league)
