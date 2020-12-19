# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 10:19:19 2020

@author: LtdDan82
@github: https://github.com/LtdDan82
"""
# Imports and global settings
import os
from PIL import Image
cwd = os.getcwd()
page_icon = os.path.join(cwd, 'img', 'unmasked_logo.PNG')

                         
import pandas as pd

import streamlit as st
st.set_page_config(page_title='Session Dashboard',
                   layout = 'wide',
                   page_icon = Image.open(page_icon),
                   initial_sidebar_state = "expanded")


#Get Final Data
from lib.data_transform import extract_transform

# Game Stats
from lib.data_analysis import get_gameStats, get_pot_stats, get_played_games, plot_played_games

# Player Stats
from lib.player_analysis import get_wins, get_raise_rate, plot_player_stats, sum_player_stats


#%%
df_final = extract_transform()
#%% Generate Game Data
game = get_played_games(df_final)
pot = get_pot_stats(df_final)

game_stats = get_gameStats(game, pot)
fig_games = plot_played_games(game)


#%% Generate Player Data
df_player_stats = sum_player_stats(df_final)
#plot the raiserate
fig_player_stats = plot_player_stats(df_player_stats)
# List of player for selection items
players = df_player_stats.index.tolist()

#%% Headline

st.write("""
         # Dashboard - Session_id #
         """)
                  
st.write("""
         ## Statistics - Game
         """)
#col1
game_col1, game_col2 = st.beta_columns([3,1])    
game_col1.table(game_stats.style.format("{:.1f}"))
#col 2
game_col2.pyplot(fig_games)

# Generate Sidebar for player selection
player = st.sidebar.selectbox('Select Player', options = players, index = 0)

opponents = st.sidebar.multiselect('Select Opponent(s)',
                                   default = players,
                                   options = players)

st.write("""
## Statistics - Players
""")

play_col1, play_col2 = st.beta_columns(2)
#col 1
play_col1.pyplot(fig_player_stats)

#df_wins, num_wins = get_wins(df_final, selection)

#msg_wins = 'Player {} win {} times this session' .format(selection, num_wins)

#col2
play_col2.write('FU')


