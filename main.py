import os
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

headers = {"User-Agent": "Mozilla/5.0"}

# Ask user for input on which year to scrape data for
while True:
    try:
        year = int(input("Enter year to scrape data for: "))
        if year < 1950 or year > 2023:  # Check if year is within valid range
            raise ValueError
        break
    except ValueError:
        print("Error: Please enter a valid year between 1950 and 2023.")

filename = f"{year}_nba_stats.csv"

# Check if the file already exists in the current directory
if os.path.isfile(filename):
    print(f"{filename} already exists, skipping download.")
else:
    # Scrape data from website
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
    source = requests.get(url, headers=headers)
    soup = BeautifulSoup(source.content, "html.parser")

    # Extract data and create DataFrame
    header = [th.getText() for th in soup.findAll("tr", limit=2)[0].findAll("th")]
    header = header[1:]
    rows = soup.findAll("tr")[1:]
    player_stats = [
        [td.getText() for td in rows[i].findAll("td")] for i in range(len(rows))
    ]
    stats = pd.DataFrame(player_stats, columns=header)

    # Replace blank cells with NaN
    stats.replace("", np.nan, inplace=True)

    # Drop rows with all NaN values
    stats.dropna(how="all", inplace=True)

    # Fill remaining NaN values with 0.0
    stats.fillna(value=0.0, inplace=True)

    # Write stats DataFrame to CSV file
    stats.to_csv(filename, index=False)
    print(f"Successfully wrote NBA stats for {year} to {filename}")

# Load data from CSV file
while True:
    try:
        stats = pd.read_csv(filename)
        break
    except FileNotFoundError:
        print(
            f"Error: {filename} not found. Please make sure you have downloaded the data for the correct year."
        )
        while True:
            try:
                year = int(input("Enter year to scrape data for: "))
                if year < 1950 or year > 2023:  # Check if year is within valid range
                    raise ValueError
                break
            except ValueError:
                print("Error: Please enter a valid year between 1950 and 2023.")
        filename = f"{year}_nba_stats.csv"

# Ask user for input on which statistic to analyze
while True:
    statistic = input(
        "Enter statistic to analyze (e.g. Pos, Age, G, GS, MP, FG, FGA, FG%, 3P, 3PA, 3P%, 2P, 2PA, 2P%, eFG%, FT, "
        "FTA, FT%, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS):"
    )
    if statistic in stats.columns:
        break
    else:
        print(f"Error: {statistic} is not a valid statistic.")

# Define a dictionary that maps each team to a specific color
team_colors = {
    "ATL": "red",
    "BOS": "green",
    "BRK": "black",
    "CHO": "turquoise",
    "CHI": "darkred",
    "CLE": "maroon",
    "DAL": "blue",
    "DEN": "darkblue",
    "DET": "darkgoldenrod",
    "GSW": "yellow",
    "HOU": "crimson",
    "IND": "navy",
    "LAC": "blue",
    "LAL": "purple",
    "MEM": "navy",
    "MIA": "pink",
    "MIL": "green",
    "MIN": "darkblue",
    "NOP": "gold",
    "NYK": "orange",
    "OKC": "orange",
    "ORL": "blue",
    "PHI": "blue",
    "PHO": "purple",
    "POR": "red",
    "SAC": "purple",
    "SAS": "gray",
    "TOR": "red",
    "UTA": "navy",
    "WAS": "navy",
}

# Group data by team and calculate average of the selected statistic
team_stats = stats[stats["Tm"] != "TOT"].groupby("Tm")[statistic].mean()

# Plot horizontal bar chart of average statistics for each team
team_stats.plot(
    kind="barh",
    figsize=(10, 8),
    color=[team_colors[x] for x in team_stats.index],
    legend=False,
)

# Set plot title and axis labels
plt.title(f"Average {statistic} for each team in {year}")
plt.xlabel(statistic)
plt.ylabel("Team")

# Show the plot
plt.show()

# Display team stats as a table
print("\nTeam Averages:\n")
team_stats_df = pd.DataFrame(team_stats).reset_index()
team_stats_df.columns = ["Team", "Average"]
print(team_stats_df.to_string(index=False))
# display(team_stats_df) (Jupyter Notebook Pandas use)

# Sort team_stats_df by the average statistic in ascending order
team_stats_df = team_stats_df.sort_values(by="Average")

# Display the team with the minimum value and its corresponding average
min_team = team_stats_df.iloc[0]["Team"]
min_value = team_stats_df.iloc[0]["Average"]
print(f"Minimum {statistic}: {min_value:.2f} (Team: {min_team})")

# Display the team with the maximum value and its corresponding average
max_team = team_stats_df.iloc[-1]["Team"]
max_value = team_stats_df.iloc[-1]["Average"]
print(f"Maximum {statistic}: {max_value:.2f} (Team: {max_team})")

# Calculate mean and standard deviation of team_stats
from scipy.stats import norm

mean = np.mean(team_stats)
std = np.std(team_stats)
print(f"Mean: {mean}")
print(f"Standard Deviation: {std}")
# Create a normal distribution object
dist = norm(mean, std)

# Generate x-values for the plot
x = np.linspace(mean - 3 * std, mean + 3 * std, 100)

# Generate the normal distribution curve
y = dist.pdf(x)

# Create a histogram of the team_stats data
plt.hist(team_stats, bins=10, density=True, alpha=0.5, label="Team Averages")

# Plot the normal distribution curve
plt.plot(x, y, label="Normal Distribution")

# Set plot title and axis labels
plt.title(f"Normal Distribution of {statistic} for each team in {year}")
plt.xlabel(statistic)
plt.ylabel("Density")

# Add a legend
plt.legend()

# Show the plot
plt.show()
