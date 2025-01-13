import tkinter as tk
from tkinter import ttk, messagebox
from nba_api.stats.endpoints import playercareerstats, playergamelog
from nba_api.stats.static import players
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Define a function to return the id of a given player
def find_player_id(name):
    try:
        player_name = players.find_players_by_full_name(name)
        return player_name[0]['id']
    except IndexError:
        return None




#  Define a function to return per-game averages for a player's 2024-25 season.


def get_season_stats(player_name):
    player_id = find_player_id(player_name)
    if player_id is None:
        return None, f"Player '{player_name}' not found."
    
    # Fetch career stats
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df_career = career.get_data_frames()[0]

    # Clean and prepare data
    df_career.columns = df_career.columns.str.lower()
    df_career.drop(columns=['league_id', 'team_id', 'player_age'], inplace=True)
    df_career.rename(columns={'team_abbreviation':'team'}, inplace=True)

    stat_columns = ['min', 'fgm', 'fga', 'fg3m', 'fg3a', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'pts']

    # Calculate average columns
    for col in stat_columns:
        avg_col_name = f"{col}_avg"  # Naming convention for average columns
        df_career[avg_col_name] = (df_career[col] / df_career['gp']).round(2)  # Divide by 'gp' to calculate per-game averages
        # avg_cols.append(avg_col_name)  # Add to the list of average columns

    # Calculate combo stats. Pts + reb, pts + ast, pts + reb + ast, reb + ast, blk + stl
    df_career['combo_pr'] = df_career.loc[:,['pts_avg','reb_avg']].sum(axis=1).round(2)
    df_career['combo_pa'] = df_career.loc[:,['pts_avg','ast_avg']].sum(axis=1).round(2)
    df_career['combo_pra'] = df_career.loc[:,['pts_avg','reb_avg','ast_avg']].sum(axis=1).round(2)
    df_career['combo_ra'] = df_career.loc[:,['reb_avg','ast_avg']].sum(axis=1).round(2)
    df_career['combo_bs'] = df_career.loc[:,['blk_avg','stl_avg']].sum(axis=1).round(2)

    # Filter for the 2024-25 season
    pg_avg_25 = df_career[df_career['season_id'] == '2024-25'][[
        'player_id', 'season_id', 'team', 'gp',
        'pts_avg', 'reb_avg', 'ast_avg', 'stl_avg', 'blk_avg',
        'combo_pr', 'combo_pa', 'combo_pra', 'combo_ra', 'combo_bs',
        'fg3m_avg', 'fg3a_avg', 'fg3_pct', 'fgm_avg', 'fga_avg', 
        'fg_pct', 'oreb_avg', 'dreb_avg', 'min_avg'
    ]]
    
    if pg_avg_25.empty:
        return None, f"No data available for player '{player_name}' in the 2024-25 season."


    # ----------Calculate averages over the player's 10, 5, and 3 recent games.----------

    career = playergamelog.PlayerGameLog(player_id=player_id)
    df_game_log = career.get_data_frames()[0]

    df_game_log.columns = df_game_log.columns.str.lower()
    df_game_log.drop(columns=['video_available'], inplace=True)

    season_avg_cols = []

    # List of columns to compute averages
    season_stat_columns = ['min', 'fgm', 'fga', 'fg3m', 'fg3a', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'pts']

    # Compute average columns
    for col in season_stat_columns:
        avg_col_name = f"{col}_avg"  # Naming convention for average columns
        df_career[avg_col_name] = (df_career[col] / df_career['gp']).round(2)  # Divide by 'gp' to calculate per-game averages
        season_avg_cols.append(avg_col_name)  # Add to the list of average columns




    # ----------Keep last 10 game log to place below the averages column.----------
    df_last_10_game_log = df_game_log[:10][[
    'game_id', 'game_date', 'matchup', 'wl',
    'pts', 'reb', 'ast', 'stl', 'blk',
    'fg3m', 'fg3a', 'fg3_pct', 'fgm', 'fga', 'fg_pct', 'ftm', 'fta', 'ft_pct',
    'oreb', 'dreb', 'min', 'tov', 'pf', 'plus_minus']]


    # List of columns to compute averages
    last_x_stat_columns = ['min', 'fgm', 'fga', 'fg3m', 'fg3a', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'pts']

    # Function to calculate averages and combo stats
    def compute_combos(df, num_games):
        
        df['num_games'] = num_games
        
        for col in last_x_stat_columns:
            df[f"{col}_avg"] = (df[col].sum() / num_games).round(2)  # Compute per-game averages
        
        # Calculate combo stats
        df['combo_pr'] = df[['pts_avg', 'reb_avg']].sum(axis=1).round(2)
        df['combo_pa'] = df[['pts_avg', 'ast_avg']].sum(axis=1).round(2)
        df['combo_pra'] = df[['pts_avg', 'reb_avg', 'ast_avg']].sum(axis=1).round(2)
        df['combo_ra'] = df[['reb_avg', 'ast_avg']].sum(axis=1).round(2)
        df['combo_bs'] = df[['blk_avg', 'stl_avg']].sum(axis=1).round(2)
        return df

    # Calculate averages and combo stats for the last 3, 5, and 10 games
    df_last_3_avg = compute_combos(df_game_log[:3], 3)[:1]
    df_last_5_avg = compute_combos(df_game_log[:5], 5)[:1]
    df_last_10_avg = compute_combos(df_game_log[:10], 10)[:1]

    last_xyz_avg = pd.concat([df_last_3_avg, df_last_5_avg, df_last_10_avg])[[
    'season_id', 'num_games',
    'pts_avg', 'reb_avg', 'ast_avg', 'stl_avg', 'blk_avg',
    'combo_pr', 'combo_pa', 'combo_pra', 'combo_ra', 'combo_bs',
    'fg3m_avg', 'fg3a_avg', 'fg3_pct', 'fgm_avg', 'fga_avg', 
    'fg_pct', 'oreb_avg', 'dreb_avg', 'min_avg']]

    


    # -------------------------- Plot stats function --------------------------
    # Function to plot stats and embed in Tkinter window
    sns.set_context("paper") 

    # Define plot columns and names
    x_col = 'game_date'
    y_cols = ['pts', 'reb', 'ast']
    y_names = ['Points', 'Rebounds', 'Assists']

    # Create a figure with 3 subplots horizontally (1 row, 3 columns)
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(10, 1))  # Adjust size of the overall figure

    for ax, col, name in zip(axes, y_cols, y_names):
        ax.plot(df_last_10_game_log[x_col], df_last_10_game_log[col], marker="o", label=col)
        ax.set_ylabel(name)
        ax.set_xticks([])
        ax.set_ylim(df_last_10_game_log[col].min() * 0.95, df_last_10_game_log[col].max() * 1.05)

        # Invert axis to easily read from left to right, giving a better idea of the player's statistical trends.
        ax.invert_xaxis()

    # Adjust space between the plots
    plt.subplots_adjust(wspace=0.3)  # Space between plots

    # Convert the plot to tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

    plt.close(fig)

    return pg_avg_25, last_xyz_avg, df_last_10_game_log, None









def show_season_stats():

    # Display the stats of the player entered in the input box.
    player_name = player_name_entry.get().strip()
    if not player_name:
        messagebox.showerror("Input Error", "Please enter a player's name.")
        return

    # Get player data
    season_stats, last_xyz_avg, df_last_10_game_log, error_message = get_season_stats(player_name)
    if error_message:
        messagebox.showerror("Error", error_message)
        return

    # Display season stats, 
    for i in season_stats_tree.get_children():
        season_stats_tree.delete(i)

    # Display per-game averages (stats)
    for _, row in season_stats.iterrows():
        season_stats_tree.insert('', 'end', values=list(row))

    # Display recent stats in the treeview
    for i in recent_stats_tree.get_children():
        recent_stats_tree.delete(i)


    # Insert data for 3, 5, and 10 game averages into recent_stats_tree
    recent_stats_tree.insert('', 'end', values=list(last_xyz_avg.iloc[0]))
    recent_stats_tree.insert('', 'end', values=list(last_xyz_avg.iloc[1]))
    recent_stats_tree.insert('', 'end', values=list(last_xyz_avg.iloc[2]))

    # Display game log
    for i in last_10_stats_tree.get_children():
        last_10_stats_tree.delete(i)
    for _, row in df_last_10_game_log.iterrows():
        last_10_stats_tree.insert('', 'end', values=list(row))








### Create an autocomplete tool for the player name entry box. Tool will look to a list of all current NBA players from the static nba-api players.get_players() function.

# Get a list of all active NBA players
all_players = players.get_players()
current_players = [player for player in all_players if player['is_active']]
player_names = [f"{player['first_name']} {player['last_name']}" for player in current_players]




# Create the autocomplete tool
class AutocompleteEntry(tk.Entry):
    def __init__(self, master=None, suggestions=[], **kwargs):
        super().__init__(master, **kwargs)
        self.suggestions = suggestions
        self.listbox = None

        self.bind("<KeyRelease>", self.on_key_release)

    # Handle key release events to display suggestions.
    def on_key_release(self, event):
       
        if self.listbox is not None:
            self.listbox.destroy()

        text = self.get()
        if not text:
            return

        # Filter matches
        matches = [s for s in self.suggestions if s.lower().startswith(text.lower())]
        if matches:
            self.listbox = tk.Listbox(self.master, height=min(len(matches), 5))
            self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
            for match in matches:
                self.listbox.insert(tk.END, match)
            
            # Bind listbox events
            self.listbox.bind("<Double-Button-1>", self.on_select)
            self.listbox.bind("<Return>", self.on_select)
            self.listbox.bind("<FocusOut>", lambda e: self.listbox.destroy())

    def on_select(self, event):
        # Handle selection from the listbox.
        if self.listbox is not None:
            index = self.listbox.curselection()
            if index:
                value = self.listbox.get(index)
                self.delete(0, tk.END)
                self.insert(0, value)
            self.listbox.destroy()





# Initialize the main window
root = tk.Tk()
root.title("NBA Player Stats Viewer")

# Create an input frame for player name and stats selection
input_frame = ttk.Frame(root, padding="10")
input_frame.grid(row=0, column=0, sticky="EW")

# Player name input using AutocompleteEntry
ttk.Label(input_frame, text="Player Name:").grid(row=0, column=0, padx=5, pady=5, sticky="W")
player_name_entry = AutocompleteEntry(input_frame, suggestions=player_names, width=16)
player_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="W")
ttk.Button(input_frame, text="Get Stats", command=show_season_stats).grid(row=0, column=2, padx=5, pady=5, sticky="W")




# Over/under combobox and integer entry
# Integer entry for O/U bets
ttk.Label(input_frame, text="Total:").grid(row=1, column=0, padx=5, pady=5, sticky="W")
total_entry = ttk.Entry(input_frame, width=16)
total_entry.grid(row=1, column=1, padx=5, pady=5, sticky="W")
over_under = ["Over", "Under"]
over_under_dropdown = ttk.Combobox(input_frame, values=over_under, width=9)
over_under_dropdown.grid(row=1, column=2, padx=5, pady=5, sticky="W")

# Metric Dropdown
ttk.Label(input_frame, text="Select stat:").grid(row=2, column=0, padx=5, pady=5, sticky="W")
stats = ["Points", "Rebounds", "Assists", "Blocks", "Steals", "PR", "PA", "PRA", "RA", "BS"]
stats_dropdown = ttk.Combobox(input_frame, values=stats, state="readonly", width=13)
stats_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="W")











# Define columns for season stats
season_columns = [
    'player_id', 'season_id', 'team', 'gp',
    'pts_avg', 'reb_avg', 'ast_avg', 'stl_avg', 'blk_avg',
    'combo_pr', 'combo_pa', 'combo_pra', 'combo_ra', 'combo_bs',
    'fg3m_avg', 'fg3a_avg', 'fg3_pct', 'fgm_avg', 'fga_avg', 
    'fg_pct', 'oreb_avg', 'dreb_avg', 'min_avg', 
]

# Define columns for recent stats
recent_columns = [
    'season_id', 'num_games',
    'pts_avg', 'reb_avg', 'ast_avg', 'stl_avg', 'blk_avg',
    'combo_pr', 'combo_pa', 'combo_pra', 'combo_ra', 'combo_bs',
    'fg3m_avg', 'fg3a_avg', 'fg3_pct', 'fgm_avg', 'fga_avg', 
    'fg_pct', 'oreb_avg', 'dreb_avg', 'min_avg'
]

# Define columns for game logs over last 10 games.
last_10_columns = [
    'game_id', 'game_date', 'matchup', 'wl',
    'pts', 'reb', 'ast', 'stl', 'blk',
    'fg3m', 'fg3a', 'fg3_pct', 'fgm', 'fga', 'fg_pct', 'ftm', 'fta', 'ft_pct',
    'oreb', 'dreb', 'min', 'tov', 'pf', 'plus_minus'
]


# Create a function to generate and configure a treeview widget
def create_treeview(parent, columns, row, col, height=15):
    tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
    tree.grid(row=row, column=col, sticky="NSEW")

    for col_name in columns:
        tree.heading(col_name, text=col_name)
        tree.column(col_name, width=100, anchor="center")

    # Scrollbars for the table
    scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    scrollbar_y.grid(row=row, column=col + 1, sticky="NS")
    tree.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
    scrollbar_x.grid(row=row + 1, column=col, sticky="EW")
    tree.configure(xscrollcommand=scrollbar_x.set)

    # Adjust row and column weights for the layout
    parent.rowconfigure(row, weight=1)
    parent.columnconfigure(col, weight=1)

    return tree



# Create the Treeview for season stats
season_stats_tree = create_treeview(root, season_columns, row=2, col=0)

# Create the Treeview for recent stats
recent_stats_tree = create_treeview(root, recent_columns, row=3, col=0)

# Create the Treeview for the game logs.
last_10_stats_tree = create_treeview(root, last_10_columns, row=4, col=0)

root.mainloop()