# ESPN Fantasy Analysis — Claude Handoff

## Project summary
This repo is a Streamlit app for ESPN Fantasy Basketball analysis. It lets a user:

- enter a league ID
- select their team and opponent
- compare matchup stats for a chosen date
- analyze 9-cat and 9-cat + 3% scoring formats
- view team radar comparison and league heatmap standings

The app is built around ESPN fantasy data and is intended for entertainment/decision support, not official analysis.

## Important files
- `streamlit_competition_selection.py` — main app/landing page and weekly analysis flow
- `team_radar_streamlit.py` — team radar chart page
- `heatmap_standings.py` — heatmap standings page
- `weekly_analysis.py` — ESPN API access, stat aggregation, category logic, matchup calculations
- `config.py` — season config with environment override via `ESPN_FANTASY_SEASON`
- `readme.md` — project overview and setup notes
- `requirements.txt` — Python dependencies

## Current app behavior
The main app in `streamlit_competition_selection.py` does the following:

1. asks for a league ID
2. validates the ID and loads teams in that league
3. lets the user select their team and opponent
4. optionally gates private teams behind a secret key from `st.secrets`
5. asks for league stat format (`9-Cat` or `9-Cat + 3%`)
6. lets the user choose a matchup date
7. loads each team’s matchup stats and displays comparison tables

There is also a sidebar menu with three pages:
- Weekly Analysis
- Team Radar Chart
- Heatmap Standing Analysis

## Run the app
Use the virtual environment already present in the repo:

```bash
cd /Users/atagunduzalp/Desktop/github_folders/espn-fantasy-analysis
source nba-env/bin/activate
streamlit run streamlit_competition_selection.py
```

If dependencies need reinstall:

```bash
source nba-env/bin/activate
pip install -r requirements.txt
```

## Season config
`config.py` sets the default season year to 2027 and supports a runtime override:

```bash
ESPN_FANTASY_SEASON=2028 streamlit run streamlit_competition_selection.py
```

## Secret handling
The app checks for:
- `OWNER_TEAMS`
- `OWNER_PASS`

These are read from Streamlit secrets in the local environment. If a selected team is in `OWNER_TEAMS`, the user is prompted for the owner password before access is allowed.

## Known repo details
- The README references `streamlit_main.py`, but the actual entry point in this workspace is `streamlit_competition_selection.py`.
- The project depends on `espn-api`, `streamlit`, `pandas`, `matplotlib`, and related analytics packages.
- Default season logic is centralized in `config.py` and used in `weekly_analysis.py`.

## Why this project matters
This app is a custom ESPN fantasy basketball toolkit focused on weekly matchup analysis, comparing production and category trends, and generating quick decision-support views for a league matchup.

## Suggested next tasks for Claude
- check if the weekly analysis flow is stable for all ESPN weeks/dates
- fix any issue with stat keys or date windows in `weekly_analysis.py`
- improve the table styling and percentage calculations
- make the app more robust with better error handling and loading states
- add tests for league/team parsing and stat aggregation logic

## Local workspace path
`/Users/atagunduzalp/Desktop/github_folders/espn-fantasy-analysis`
