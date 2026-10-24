# 🏀 ESPN Fantasy Basketball Analysis Tool

A Streamlit application designed to give you a competitive edge in ESPN Fantasy Basketball. Analyze matchups, visualize league standings, and find the perfect waiver wire pickups.

## ✨ Features

- **🔥 Smart Waiver Recommendations**: Automatically suggests free agents who excel in the specific categories where your current matchup is close.
- **📊 Weekly Matchup Analysis**: Predicts match results based on player schedules and recent performance for 9-cat and 9-cat+3% formats.
- **🏆 League Standings Heatmap**: Visualize the strengths and weaknesses of every team in your league with an interactive heatmap.
- **🕸️ Team Radar Comparison**: Detailed statistical comparison between two teams using radar charts.

## 🚀 Installation & Usage

```bash
# 1. Clone the repository
git clone https://github.com/atagunduzalp/espn-fantasy-analysis.git
cd espn-fantasy-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run streamlit_competition_selection.py
```

## 📱 How to Use

1. **Select a Tool**: Choose from the sidebar menu:
   - **Weekly Analysis**: See who wins the week and get **Smart Waiver** tips.
   - **Heatmap Standings**: See the league meta.
   - **Team Radar**: Head-to-head stat comparison.
2. **Enter Details**: Provide your League ID. The default season is set in `config.py` and can be overridden with `ESPN_FANTASY_SEASON`.
3. **Dominate**: Use the insights to set your lineup and make moves.

### Season override

```bash
ESPN_FANTASY_SEASON=2028 streamlit run streamlit_competition_selection.py
```

---

**Note**: This tool is for entertainment and analytical purposes. Not officially affiliated with ESPN.
