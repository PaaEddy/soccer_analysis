import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Data path folder
data_folder = 'data'

# Step 2: Read and combine all CSV files in the data folder
all_files = pd.concat([
    pd.read_csv(os.path.join(data_folder, file))
    for file in os.listdir(data_folder) if file.endswith('.csv')
], ignore_index=True)

# Step 3: Preview combined data
combined_preview = all_files[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]].head()

# Step 4: Convert 'Date' to datetime
all_files['Date'] = pd.to_datetime(all_files['Date'], dayfirst=True)
all_files['Season'] = all_files['Date'].dt.year

# Step 5: Process each season file individually
season_files = {
    '2020-2021': 'data_epl_2020_2021.csv',
    '2021-2022': 'data_epl_2021_2022.csv',
    '2022-2023': 'data_epl_2022_2023.csv',
    '2023-2024': 'data_epl_2023_2024.csv',
    '2024-2025': 'data_epl_2024_2025.csv'
}

season_stats = []

for season, file_name in season_files.items():
    file_path = os.path.join(data_folder, file_name)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Season'] = season
        df['TotalGoals'] = df['FTHG'] + df['FTAG']
        
        goals_scored = df.groupby('HomeTeam')['FTHG'].sum() + df.groupby('AwayTeam')['FTAG'].sum()
        goals_scored = goals_scored.reset_index()
        goals_scored.columns = ['Team', 'GoalsScored']
        
        goals_conceded = df.groupby('HomeTeam')['FTAG'].sum() + df.groupby('AwayTeam')['FTHG'].sum()
        goals_conceded = goals_conceded.reset_index()
        goals_conceded.columns = ['Team', 'GoalsConceded']
        
        top_scorers = goals_scored.sort_values(by='GoalsScored', ascending=False).head(10)
        top_conceders = goals_conceded.sort_values(by='GoalsConceded', ascending=False).head(10)
        
        season_stats.append({
            'Season': season,
            'TotalGoals': df['TotalGoals'].sum(),
            'TopScorers': top_scorers,
            'TopConceders': top_conceders
        })

# Aggregate total goals scored per team (home + away)
scored_home = all_files.groupby('HomeTeam')['FTHG'].sum()
scored_away = all_files.groupby('AwayTeam')['FTAG'].sum()
total_scored = scored_home.add(scored_away, fill_value=0).reset_index()
total_scored.columns = ['Team', 'GoalsScored']

# Aggregate total goals conceded per team (home + away)
conceded_home = all_files.groupby('HomeTeam')['FTAG'].sum()
conceded_away = all_files.groupby('AwayTeam')['FTHG'].sum()
total_conceded = conceded_home.add(conceded_away, fill_value=0).reset_index()
total_conceded.columns = ['Team', 'GoalsConceded']

# Merge to single DataFrame for plotting
team_stats_df = pd.merge(total_scored, total_conceded, on='Team')
top_scorers = team_stats_df.sort_values(by='GoalsScored', ascending=False).head(10)
top_conceders = team_stats_df.sort_values(by='GoalsConceded', ascending=False).head(10)


# Create a DataFrame for goals comparison
goals_comparison = pd.DataFrame({
    'Season': [stat['Season'] for stat in season_stats],
    'TotalGoals': [stat['TotalGoals'] for stat in season_stats]
})

# Plotting Total Goals per Season
plt.figure(figsize=(10, 6))
plt.bar(goals_comparison['Season'], goals_comparison['TotalGoals'], color='skyblue')
plt.title('Total Goals per EPL Season (2020-2025)')
plt.ylabel('Total Goals')
plt.xlabel('Season')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('total_goals_per_season.png')
plt.close()


# Convert top scorers and conceders to CSV and save
scorers_csv = []
conceders_csv = []
for stat in season_stats:
    top_scorers_df = stat['TopScorers'].copy()
    top_scorers_df['Season'] = stat['Season']
    scorers_csv.append(top_scorers_df)

    top_conceders_df = stat['TopConceders'].copy()
    top_conceders_df['Season'] = stat['Season']
    conceders_csv.append(top_conceders_df)

scorers_result = pd.concat(scorers_csv)
conceders_result = pd.concat(conceders_csv)

scorers_result.to_csv('top_10_scorers_by_season.csv', index=False)
conceders_result.to_csv('top_10_conceders_by_season.csv', index=False)
goals_comparison.to_csv('season_goals_comparison.csv', index=False)

print("\n=== Season Goals Comparison ===")
print(goals_comparison)

# Optionally save to CSV
goals_comparison.to_csv("goals_comparison_by_season.csv", index=False)

# Create a directory to store plots if it doesn't exist
plot_folder = 'plots'
os.makedirs(plot_folder, exist_ok=True)

for season_data in season_stats:
    season_name = season_data['Season']
    top_scorers = season_data['TopScorers']
    top_conceders = season_data['TopConceders']

    # Save top scorers and conceders data for each season
    top_scorers.to_csv(os.path.join(plot_folder, f'{season_name}_top_scorers.csv'), index=False)
    top_conceders.to_csv(os.path.join(plot_folder, f'{season_name}_top_conceders.csv'), index=False)

    # Plot top scorers
    plt.figure(figsize=(10, 6))
    plt.bar(top_scorers['Team'], top_scorers['GoalsScored'], color='green')
    plt.title(f'Top 10 Teams by Goals Scored – {season_name}')
    plt.xlabel('Team')
    plt.ylabel('Goals Scored')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    scorer_plot_path = os.path.join(plot_folder, f'{season_name}_top_scorers.png')
    plt.savefig(scorer_plot_path)
    

    # Plot top conceders
    plt.figure(figsize=(10, 6))
    plt.bar(top_conceders['Team'], top_conceders['GoalsConceded'], color='lightcoral')
    plt.title(f'Top 10 Teams by Goals Conceded – {season_name}')
    plt.xlabel('Team')
    plt.ylabel('Goals Conceded')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    conceder_plot_path = os.path.join(plot_folder, f'{season_name}_top_conceders.png')
    plt.savefig(conceder_plot_path)
    


# Load full data again (assume it was already concatenated into all_files.csv previously for analysis)

df = all_files.copy()

# Convert Date column if it exists
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

# Clean sheet indicator
df['HomeCleanSheet'] = df['FTAG'] == 0
df['AwayCleanSheet'] = df['FTHG'] == 0

# Match result counts
result_counts = df['FTR'].value_counts()

# Clean sheet share
clean_sheets = pd.DataFrame({
    'Home': df['HomeCleanSheet'].sum(),
    'Away': df['AwayCleanSheet'].sum()
}, index=['CleanSheets']).T

# Goals per team (line chart data)
home_goals = df.groupby(['Date', 'HomeTeam'])['FTHG'].sum().reset_index()
away_goals = df.groupby(['Date', 'AwayTeam'])['FTAG'].sum().reset_index()
home_goals.columns = ['Date', 'Team', 'Goals']
away_goals.columns = ['Date', 'Team', 'Goals']
goals_over_time = pd.concat([home_goals, away_goals])
goals_over_time = goals_over_time.groupby(['Date', 'Team'])['Goals'].sum().reset_index()

# Heatmap: Goals scored vs. opponent
heatmap_data = df.pivot_table(index='HomeTeam', columns='AwayTeam', values='FTHG', aggfunc='sum', fill_value=0)

# Shot accuracy vs. total goals as proxy for points
df['HShotAcc'] = df['HST'] / df['HS']
df['AShotAcc'] = df['AST'] / df['AS']
df.replace([float('inf'), -float('inf')], 0, inplace=True)

shot_accuracy = pd.DataFrame({
    'Team': pd.concat([df['HomeTeam'], df['AwayTeam']]),
    'Accuracy': pd.concat([df['HShotAcc'], df['AShotAcc']]),
    'Goals': pd.concat([df['FTHG'], df['FTAG']])
})

shot_accuracy_grouped = shot_accuracy.groupby('Team').mean().reset_index()


# Plot 4: Heatmap of goals vs. opponent
plt.figure(figsize=(12, 10))
sns.heatmap(heatmap_data, cmap='Reds', annot=False)
plt.title("Goals Scored vs. Opponent (Home Perspective)")
plt.xlabel("Away Team")
plt.ylabel("Home Team")
plt.tight_layout()
plt.savefig(f"{plot_folder}/goal_heatmap.png")
plt.close()


# Plot 5: Scatter plot of shot accuracy vs. goals
plt.figure(figsize=(8, 6))
sns.scatterplot(data=shot_accuracy_grouped, x='Accuracy', y='Goals')
plt.title("Shot Accuracy vs. Goals")
plt.xlabel("Average Shot Accuracy")
plt.ylabel("Average Goals")
plt.tight_layout()
plt.savefig(f"{plot_folder}/accuracy_vs_goals.png")
plt.close()