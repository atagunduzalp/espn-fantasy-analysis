from espn_api.basketball import League, Player, Team
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import datetime
import pytz
import streamlit as st
from datetime import date

# TO_DO
# streamlit formatında tarih, takım ismi, rakip takım ve lig id bilgisi al

# 8li fantasy --> 640492668
# bizimki --> 170805702

# date = datetime.datetime.today()


# date = datetime.datetime(2024, 10, 28)
# league = League(league_id=170805702, year=2025, debug=False)
# player = Player(data = {'name':'Jayson Tatum'}, year=2025)

nine_cat_stats = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', '3PM', 'FGM', 'FGA', 'FTM', 'FTA']
# MY_TEAM = 'Los Black Mamba'
# OPPONENT_TEAM = 'Balabumbar'

def is_within_week(date_dict, param_date, player):
    # eastern = pytz.timezone('America/New_York')

    if isinstance(param_date, datetime.date) and not isinstance(param_date, datetime.datetime):
        param_date = datetime.datetime.combine(param_date, datetime.datetime.min.time())

    day_of_week = param_date.weekday()  # 0 = Pazartesi, 6 = Pazar

    # Haftanın başlangıç tarihi (Pazartesi)
    start_of_week = param_date - datetime.timedelta(days=day_of_week)

    # Haftanın bitiş tarihi (Pazar)
    # end_of_week = start_of_week + datetime.timedelta(days=7)
    end_of_week = start_of_week + datetime.timedelta(days=7, hours=7, minutes=59, seconds=59)

    today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

    count = 0
    for date_elem in date_dict:
        match_date = date_dict[date_elem]['date']
        if isinstance(match_date, datetime.date) and not isinstance(match_date, datetime.datetime):
            match_date = datetime.datetime.combine(match_date, datetime.datetime.min.time())
        # `match_date`'i Doğu saatine göre ayarla
        # match_date = eastern.localize(match_date)

        if today <= match_date <= end_of_week:
            count += 1

    return count

def get_league_info(league_id):
    return League(league_id=league_id, year=2025, debug=False)


def get_teams_stats(league_id, team_name, date, league):
    # league = get_league_info(league_id)
    all_players_stats_dict = {}

    current_stats = current_state(team_name, league)

    for team in league.teams:
        if team.team_name == team_name:
            roster = team.roster
            stat_dict = {}
            for player in roster:
                if player.injuryStatus != 'OUT':
                    player_stats_dict = {}

                    match_count = is_within_week(player.schedule, date, player)
                    if player.stats is not None:
                        last_15_days_avg = {}
                        for key in nine_cat_stats:
                            if '2025_last_15' in player.stats:
                                # '2025_projected' '2024_last_15'
                                if len(player.stats['2025_last_15']) > 4:
                                    if key in player.stats['2025_last_15']['avg']:
                                        stat_dict[key] = player.stats['2025_last_15']['avg'][key] * match_count
                                        last_15_days_avg[key] = player.stats['2025_last_15']['avg'][key] * match_count
                                    else:
                                        last_15_days_avg[key] = 0

                        percentage_calculation(last_15_days_avg)

                        player_stats_dict['2025_last_15'] = last_15_days_avg
                        # all_players_stats_dict[player.name] = player_stats_dict
                        all_players_stats_dict[player.name] = last_15_days_avg
    print(all_players_stats_dict)
    all_players_stats_dict['current'] = current_stats
    df = pd.DataFrame(all_players_stats_dict)
    # df['remaining'] = df.drop(columns=['current']).sum(axis=1)
    df['total'] = df.sum(axis=1)
    # df['total']['%FG'] =df['total']['FGM'] / df['total']['FGA']
    df.loc['%FG', "total"] = df['total']['FGM'] / df['total']['FGA']
    # df['total']['%FT'] = df['total']['FTM'] / df['total']['FTA']
    df.loc['%FT', "total"] = df['total']['FTM'] / df['total']['FTA']

    st.write(df)
    print(df[['current', 'total']])
    # print(df)


def percentage_calculation(stats):
    try:
        # Floor Division : Gives only Fractional Part as Answer

        if stats is not None and 'FGA' in stats.keys():
            stats['%FG'] = stats['FGM'] / stats['FGA']
        if stats is not None and 'FTA' in stats.keys():
            stats['%FT'] = stats['FTM'] / stats['FTA']
    except ZeroDivisionError:
        print("Sorry ! You are dividing by zero ")


def current_state(team_name, league):
    current_away_stats = {}
    current_home_stats = {}
    box_score = league.box_scores()
    for game in box_score:
        if game.home_team.team_name == team_name:
            home_stat = game.home_stats
            if len(home_stat) > 0:
                for key in nine_cat_stats:
                    current_home_stats[key] = home_stat.get(key)['value']
                percentage_calculation(current_home_stats)
            return current_home_stats
        elif game.away_team.team_name == team_name:
            away_stat = game.away_stats
            if len(away_stat) > 0:
                for key in nine_cat_stats:
                    if key == '3PTM':
                        key = '3PM'
                    current_away_stats[key] = away_stat.get(key)['value']
                percentage_calculation(current_away_stats)
            return current_away_stats


if __name__ == '__main__':
    date = datetime.datetime(2024, 11, 25)
    #24662177
    league_id = '170805702'
    # league = League(league_id= league_id, year=2025, debug=False)
    league = get_league_info(league_id)
    MY_TEAM = 'Los Black Mamba'
    OPPONENT_TEAM = "Burak's 6'Under"
    # MY_TEAM = 'Vinsanity Carter '
    team_stats = get_teams_stats(league_id, MY_TEAM, date, league)
    away_team_stats = get_teams_stats(league_id, OPPONENT_TEAM, date, league)