import pandas as pd
import streamlit as st
from utils import percentage_calculation
from espn_api.basketball import League
import datetime
import pytz

def recommend_players(league, close_categories, limit=10):
    """
    Fetches free agents and recommends players based on 'close_categories'.
    
    Args:
        league: The ESPN League object.
        close_categories (list): List of categories (e.g., ['BLK', 'STL']) that are close.
        limit (int): Number of players to recommend.
        
    Returns:
        pd.DataFrame: A DataFrame of recommended players with their stats.
    """
    if not close_categories:
        return pd.DataFrame()

    # 1. Fetch Top 200 Free Agents (based on season average or current form)
    # We use 'size=200' to get a decent pool. 
    # We can fetch stats for '2026_last_15' or '2026_last_30' ideally, 
    # but 'free_agents' returns a list of Player objects.
    # We need to ensure we have the stats we need.
    
    # Note: league.free_agents() returns Player objects.
    # We will look at their '2026_projected' or '2026_last_15' if available, 
    # but often standard 'stats' attribute has the season avg.
    # Let's assume we want to base this on "Last 15 Days" if possible for recent form,
    # or "Season" if that's safer. Let's stick to what weekly_analysis uses if possible.
    # For simplicity and speed, let's use the default stats available on the player object first.
    
    free_agents = league.free_agents(size=200)
    free_agents = [player for player in free_agents if not player.injured]

    data = []
    for player in free_agents:
        # Extract stats. 
        
        # Try to find the most relevant stats.
        # Based on weekly_analysis.py, keys like '2026_last_15' exist.
        # '2026_projected' usually holds season averages/projections.
        # '2026_total' might hold total season stats.
        
        player_stats = {}
        
        # Priority 1: Averages (Most stable)
        
        if '2026_last_15' in player.stats and 'avg' in player.stats['2026_last_15']:
             player_stats = player.stats['2026_last_15']['avg'].copy()
             
             # Calculate percentages using shared utility
             percentage_calculation(player_stats)
        
        row = {
            "Name": player.name, 
            "Position": player.position, 
            "Team": player.proTeam
        }
        
        # Add all category stats to the row
        for cat in close_categories:
            val = player_stats.get(cat, 0)
            row[cat] = val
            
        data.append(row)

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    # 2. Normalization & Scoring
    # We only care about 'close_categories'.
    
    # Create a score column
    df['Score'] = 0.0
    
    for cat in close_categories:
        # Skip if category not in df (e.g. if it's a weird cat like FGM/FGA split)
        if cat not in df.columns:
            continue
            
        # Get Max value in this batch for normalization
        max_val = df[cat].max()
        
        # Avoid division by zero
        if max_val == 0:
            continue
            
        # Normalize: Value / Max
        # Note: For TO (Turnovers), Lower is Better. 
        # But usually "Close Category" means we want to WIN it.
        # If we want to win TO, we want LOW TO.
        # So for TO, the score should be (Min / Value) or (1 - (Value/Max)).
        # Let's handle TO specifically.
        
        if cat == 'TO':
            # For TO: Less is more. 
            # Let's use 1 - (Value / Max) to favor low TO players.
            df[f'{cat}_score'] = 1 - (df[cat] / max_val)
        else:
            # For PTS, REB, etc: More is better.
            df[f'{cat}_score'] = df[cat] / max_val
            
        # Add to total score
        df['Score'] += df[f'{cat}_score']

    # 3. Sort and Filter
    df = df.sort_values(by='Score', ascending=False)
    print(df)
    
    # Return full sorted DataFrame (UI will handle pagination)
    cols = ['Name', 'Position', 'Team'] + close_categories + ['Score']
    return df[cols]

# test purpose
# if __name__ == '__main__':
#     league = League(league_id='170805702', year=2026, debug=False)
#     close_cats = ['BLK','REB', 'TO', '%FG']
#     recommend_players(league, close_cats, limit=10)