from espn_api.basketball import League, Player, Team
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import datetime
import streamlit as st
import pytz

nine_cat_stats = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', '3PM', 'FGM', 'FGA', 'FTM', 'FTA']
three_point_percentage_league = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', '3PM', '3PA','FGM', 'FGA', 'FTM', 'FTA' ]

def get_teams_in_league(league_id):
    league = get_league_info(league_id)
    team_list = []
    for team in league.teams:
        team_list.append(team.team_name)
    return team_list


def is_within_week(date_dict, param_date):
    # eastern = pytz.timezone('America/New_York')
    local_tz = pytz.timezone('America/New_York')

    if isinstance(param_date, datetime.date) and not isinstance(param_date, datetime.datetime):
        param_date = datetime.datetime.combine(param_date, datetime.datetime.min.time())
    param_date = local_tz.localize(param_date)


    day_of_week = param_date.weekday()  # 0 = Pazartesi, 6 = Pazar

    # Haftanın başlangıç tarihi (Pazartesi)
    start_of_week = param_date - datetime.timedelta(days=day_of_week)
    start_of_week = start_of_week + datetime.timedelta(days=0, hours=7, minutes=59, seconds=59)

    # Haftanın bitiş tarihi (Pazar)
    end_of_week = start_of_week + datetime.timedelta(days=7, hours=7, minutes=59, seconds=59)

    today = datetime.datetime.now(local_tz)

    count = 0
    for date_elem in date_dict:
        match_date = date_dict[date_elem]['date']
        if isinstance(match_date, datetime.date) and not isinstance(match_date, datetime.datetime):
            match_date = datetime.datetime.combine(match_date, datetime.datetime.min.time())
        if match_date.tzinfo is None:
            match_date = local_tz.localize(match_date)
        # `match_date`'i Doğu saatine göre ayarla
        # match_date = eastern.localize(match_date)

        if today <= match_date <= end_of_week:
            count += 1

    return count


def get_league_info(league_id):
    return League(league_id=league_id, year=2026, debug=False)


def get_teams_stats(team_name, date, league, stats_type):

    all_players_stats_dict = {}
    category_stats = {}

    stat_selection, is_3_percentage = get_selected_stat(stats_type)
    current_stats = current_state(team_name, league, date, stat_selection)

    for team in league.teams:
        if team.team_name == team_name:
            category_stats = category_analysis(team, team_name)
            roster = team.roster
            stat_dict = {}
            for player in roster:
                if player.injuryStatus != 'OUT':
                    player_stats_dict = {}

                    match_count = is_within_week(player.schedule, date)
                    if player.stats is not None:
                        last_15_days_avg = {}
                        for key in stat_selection:
                            if '2026_last_15' in player.stats:
                                # '2026_projected' '2024_last_15'
                                if len(player.stats['2026_last_15']) > 4:
                                    if key in player.stats['2026_last_15']['avg']:
                                        stat_dict[key] = player.stats['2026_last_15']['avg'][key] * match_count
                                        last_15_days_avg[key] = player.stats['2026_last_15']['avg'][key] * match_count
                                    else:
                                        last_15_days_avg[key] = 0

                        percentage_calculation(last_15_days_avg)

                        last_15_days_avg['match_count'] = match_count
                        player_stats_dict['2026_last_15'] = last_15_days_avg
                        all_players_stats_dict[player.name] = last_15_days_avg
    # print(all_players_stats_dict)
    all_players_stats_dict['current'] = current_stats
    df = pd.DataFrame(all_players_stats_dict)
    df['total'] = df.sum(axis=1)
    df.loc['%FG', "total"] = df['total']['FGM'] / df['total']['FGA']
    df.loc['%FT', "total"] = df['total']['FTM'] / df['total']['FTA']
    if is_3_percentage:
        df.loc['%3PM', "total"] = df['total']['3PM'] / df['total']['3PA']


    st.write(df)
    st.write("Team's category results" + str(category_stats))

def category_analysis(team, team_name):
    stat_dict = {}
    week_count = 0
    schedule = team.schedule
    for ones in schedule:
        if ones.winner == 'UNDECIDED':
            break
        else:
            week_count += 1
            if ones.away_team.team_name == team_name:
                team_cats = ones.away_team_cats
            elif ones.home_team.team_name == team_name:
                team_cats = ones.home_team_cats
            else:
                continue
            for stat_name in team_cats:
                stat = team_cats[stat_name]
                if stat['result'] == 'WIN':
                    if stat_name in stat_dict.keys():
                        stat_dict[stat_name] = 1 + stat_dict[stat_name]
                    else:
                        stat_dict[stat_name] = 1
    stat_dict['week_count'] = week_count
    return stat_dict

def get_selected_stat(league_stat):
    if league_stat== '9-Cat':
        return nine_cat_stats, False
    elif league_stat== '9-Cat + 3%':
        return three_point_percentage_league, True

def percentage_calculation(stats):
    try:
        # Floor Division : Gives only Fractional Part as Answer

        if stats is not None and 'FGA' in stats.keys():
            stats['%FG'] = stats['FGM'] / stats['FGA']
        if stats is not None and 'FTA' in stats.keys():
            stats['%FT'] = stats['FTM'] / stats['FTA']
        if stats is not None and '3PA' in stats.keys():
            stats['%3PM'] = stats['3PM'] / stats['3PA']

    except ZeroDivisionError:
        print("Sorry ! You are dividing by zero ")


def current_state(team_name, league, date, stat_selection):
    current_team_stats = {}

    if is_date_in_current_week(date):
        box_score = league.box_scores()
        for game in box_score:
            if game.home_team.team_name == team_name:
                team_stats = game.home_stats
            elif game.away_team.team_name == team_name:
                team_stats = game.away_stats
            else:
                continue

            if len(team_stats) > 0:
                for key in stat_selection:
                    if key == '3PTM':
                        key = '3PM'
                    current_team_stats[key] = team_stats.get(key)['value']
                percentage_calculation(current_team_stats)
            return current_team_stats
    return current_team_stats

def is_date_in_current_week(date_to_check):
    import datetime
    today = datetime.datetime.today()

    if isinstance(date_to_check, datetime.date) and not isinstance(date_to_check, datetime.datetime):
        date_to_check = datetime.datetime.combine(date_to_check, datetime.datetime.min.time())

    start_of_week = today - datetime.timedelta(days=today.weekday())  # Pazartesi 00:00
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    end_of_week = start_of_week + datetime.timedelta(days=6, hours=23,minutes=59, seconds=59)

    return start_of_week <= date_to_check <= end_of_week