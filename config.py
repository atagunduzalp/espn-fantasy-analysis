import os

DEFAULT_SEASON = 2027


def get_season():
    """Return the ESPN fantasy season to use for League() requests.

    This allows runtime overrides such as:
        ESPN_FANTASY_SEASON=2028 streamlit run streamlit_competition_selection.py
    """
    raw_value = os.getenv("ESPN_FANTASY_SEASON", DEFAULT_SEASON)
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return DEFAULT_SEASON
