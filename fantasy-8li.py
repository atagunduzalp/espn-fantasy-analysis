from os.path import split

from espn_api.basketball import League, Player, Team
import pandas as pd
import datetime

# TO_DO
# streamlit formatında tarih, takım ismi, rakip takım ve lig id bilgisi al

#8li fantasy --> 640492668
#bizimki --> 170805702

# date = datetime.datetime.today()
date = datetime.datetime(2024, 11, 25)
league = League(league_id=640492668, year=2025, debug=False)

# player = Player(data = {'name':'Jayson Tatum'}, year=2025)
# keys = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FGM', 'FGA', 'FTM', 'FTA', '3PTM', '3PTA', 'FG%', 'FT%', '3PT%']
# nine_cat_stats = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', '3PTM', 'FGM', 'FGA', 'FTM', 'FTA']


nine_cat_stats = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', '3PTM', 'FGM', 'FGA', 'FTM', 'FTA']
three_point_percentage_league = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FG%', 'FT%', '3PM', '3PA','FGM', 'FGA', 'FTM', 'FTA' ]

# MY_TEAM = 'Los Black Mamba'
# OPPONENT_TEAM = 'Balabumbar'

MY_TEAM = 'Team Black Mamba'
OPPONENT_TEAM = "Ankara Hotdogs"


def is_within_week(date_dict, param_date):
    # eastern = pytz.timezone('America/New_York')

    if isinstance(param_date, datetime.date) and not isinstance(param_date, datetime.datetime):
        param_date = datetime.datetime.combine(param_date, datetime.datetime.min.time())

    day_of_week = param_date.weekday()  # 0 = Pazartesi, 6 = Pazar

    # Haftanın başlangıç tarihi (Pazartesi)
    start_of_week = param_date - datetime.timedelta(days=day_of_week)

    # Haftanın bitiş tarihi (Pazar)
    # end_of_week = start_of_week + datetime.timedelta(days=7)
    end_of_week = start_of_week + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)

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

def percentage_calculation(stats):
    try:
        # Floor Division : Gives only Fractional Part as Answer

        if stats is not None and 'FGA' in stats.keys():
            stats['%FG'] = stats['FGM'] / stats['FGA']
        if stats is not None and 'FTA' in stats.keys():
            stats['%FT'] = stats['FTM'] / stats['FTA']
    except ZeroDivisionError:
        print("Sorry ! You are dividing by zero ")


def get_teams_stats(team_name):
    all_players_stats_dict = {}
    current_stats = current_state(team_name, league)


    for team in league.teams:
        if team.team_name == team_name:
            roster = team.roster
            total_key_value_dict = {}
            stat_dict = {}
            for player in roster:
                if player.injuryStatus != 'OUT':
                    player_stats_dict = {}
                    total_projected = 0

                    match_count = is_within_week(player.schedule, date)
                    # print(match_count)
                    # print(player.name)
                    if player.stats is not None:
                        last_15_days_avg = {}
                        for key in three_point_percentage_league:
                            if '2025_last_15' in player.stats:
                                #'2025_projected' '2024_last_15'
                                if len(player.stats['2025_last_15']) > 4:
                                    if key in player.stats['2025_last_15']['avg']:
                                        stat_dict[key] = player.stats['2025_last_15']['avg'][key] * match_count
                                        last_15_days_avg[key] = player.stats['2025_last_15']['avg'][key] * match_count
                                    else:
                                        last_15_days_avg[key] = 0

                        try:
                            # Floor Division : Gives only Fractional Part as Answer
                            if 'FGA' in last_15_days_avg.keys():
                                last_15_days_avg['%FG'] = last_15_days_avg['FGM'] / last_15_days_avg['FGA']
                            if 'FTA' in last_15_days_avg.keys():
                                last_15_days_avg['%FT'] = last_15_days_avg['FTM'] / last_15_days_avg['FTA']
                            if 'FTA' in last_15_days_avg.keys():
                                last_15_days_avg['%3'] = last_15_days_avg['3PM'] / last_15_days_avg['3PA']
                            # last_15_days_avg['%3'] = last_15_days_avg['3PM'] / last_15_days_avg['3PA']
                        except ZeroDivisionError:
                            print("Sorry ! You are dividing by zero ")

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
    df.loc['%3', "total"] = df['total']['3PM'] / df['total']['3PA']

    print(df['total'])


def current_state(team_name, league):
    current_away_stats = {}
    current_home_stats = {}
    box_score = league.box_scores()
    for game in box_score:
        if game.home_team.team_name == team_name:
            home_stat = game.home_stats
            if len(home_stat) > 0:
                for key in three_point_percentage_league:
                    current_home_stats[key] = home_stat.get(key)['value']
            return current_home_stats
        elif game.away_team.team_name == team_name:
            away_stat = game.away_stats
            if len(away_stat) > 0:
                for key in three_point_percentage_league:
                    if key == '3PTM':
                        key = '3PM'
                    current_away_stats[key] = away_stat.get(key)['value']
            return current_away_stats


if __name__ == '__main__':
    team_stats = get_teams_stats(MY_TEAM)
    away_team_stats = get_teams_stats(OPPONENT_TEAM)
