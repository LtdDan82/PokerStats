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



#%%
@st.cache(allow_output_mutation=True)
def load_dataset():
    df_final = extract_transform()
    return df_final

#%%
@st.cache(allow_output_mutation=True)
def load_gamestats():
    #get the class instance
    gamestats = GameStats(df_final)
    
    #add stuff to load here
    game = gamestats.get_played_games()
    pot = gamestats.get_pot_stats()
    general_gStats = gamestats.get_gameStats(game, pot)
    fig_played_games = gamestats.plot_played_games()
    return gamestats, general_gStats, fig_played_games

@st.cache(allow_output_mutation=True)
def load_playstats():
    #get the class instance
    playstats = PlayerStats(df_final)
    
    #add stuff to load here
    fig_play_stats = playstats.plot_player_stats()
    
    return playstats,  fig_play_stats
#%%
# def display_fig_in_app(fig_object):
#     return fig_object

#%% Load Stuff in Cache
df_final = load_dataset()

gamestats, general_gStats, fig_played_games = load_gamestats()

playstats, fig_play_stats = load_playstats()

#%% Headline
st.write("""# Dashboard - Session_id #""") 

# Generate Sidebar for player selection
players = playstats.get_ListOfPlayers()    
player = st.sidebar.selectbox('Select Player', options = players, index = 0)
opponents = st.sidebar.multiselect('Select Opponent(s)',
                                    default = players,
                                    options = players)


st.write("""### Player Stats for player: """, player) #Player Statistics
play_col1, play_col2 = st.beta_columns(2) # Generate 2 equidistant columns
specific_stats = playstats._player_specific_stats(player)
play_col1.table(specific_stats)
play_col2.write('## Visualisierung_Platzhalter')


st.write("""### Global Game Stats""") # Game Statistics
game_col1, game_col2 = st.beta_columns([3, 1]) # Generate 2 columns

game_col1.table(general_gStats.style.format("{:.1f}"))


game_col1.pyplot(fig_play_stats)
game_col2.pyplot(fig_played_games)




