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
from lib.data_analysis import GameStats
# Player Specific Stats
from lib.player_spec_analysis import PlayerStats

from lib.fig_table_styles import highlight_max, highlight_min


#%%
@st.cache(allow_output_mutation=True)
def load_dataset(datestring):
    df_final = extract_transform(datestring)
    return df_final

#%%
@st.cache(allow_output_mutation=True)
def load_gamestats(gamestats):
    #get the class instance
    #gamestats = GameStats(df_final)
    
    #add stuff to load here
    game = gamestats.get_played_games()
    pot = gamestats.get_pot_stats()
    general_gStats = gamestats.get_gameStats(game, pot)
    fig_played_games = gamestats.plot_played_games()
    return general_gStats, fig_played_games

@st.cache(allow_output_mutation=True)
def load_playstats(playstats):
    #get the class instance
    #playstats = PlayerStats(df_final)
    
    #add stuff to load here
    fig_play_stats = playstats.plot_player_stats()
    cashgame_stats = playstats.get_cashgame_statistics()
    
    return cashgame_stats, fig_play_stats

#%% Load Stuff in Cache
datestring = st.sidebar.selectbox('Select a session', options = ['12122020', '19122020'],
                                  index = 0)


df_final = load_dataset(datestring)

gamestats = GameStats(df_final)
playstats = PlayerStats(df_final)

general_gStats, fig_played_games = load_gamestats(gamestats)

cashgame_stats, fig_play_stats = load_playstats(playstats)

#%% Headline
st.write("""# Dashboard - Session_id #""") 

# Generate Sidebar for player selection
players = playstats.get_ListOfPlayers()    
selected_player = st.sidebar.selectbox('Select Player(s)', options = players,
                                       index = 0)
opponents = st.sidebar.multiselect('Select Opponent(s)',
                                    default = players,
                                    options = players)

player_vs_opp = list(set([selected_player] + opponents))


st.write("""### Player Stats for player: """, selected_player) #Player Statistics
#play_col1, play_col2 = st.beta_columns(2) # Generate 2 equidistant columns
#specific_stats = playstats._player_specific_stats(selected_player)
#play_col1.dataframe(specific_stats)

cashgame_stats = cashgame_stats.loc[player_vs_opp, :]
cashstats_styled = (cashgame_stats.style
              .apply(highlight_max)
              .apply(highlight_min)
              .format("{:.2f}")
              .set_properties(**{'text-align': 'center'})
              .set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
              )


st.dataframe(cashstats_styled)




st.write("""### Global Game Stats""") # Game Statistics
game_col1, game_col2 = st.beta_columns([2, 1]) # Generate 2 columns

gStats_styled = (general_gStats.style
              .apply(highlight_max)
              .apply(highlight_min)
              .format("{:.0f}")
              .set_properties(**{'text-align': 'center'})
              .set_table_styles([dict(selector='th', props=[('text-align', 'center')])]))

game_col1.dataframe(gStats_styled)
                

game_col1.pyplot(fig_play_stats)
game_col2.pyplot(fig_played_games)




