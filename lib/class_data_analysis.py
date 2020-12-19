# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 09:02:50 2020

@author: LtdDan82
@github: https://github.com/LtdDan82
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from lib.data_transform import extract_transform

plt.style.use('ggplot')

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Ubuntu'
plt.rcParams['font.monospace'] = 'Ubuntu Mono'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['figure.titlesize'] = 14

# Set an aspect ratio
#width, height = plt.figaspect(16/9)

#%%
class PokerSession(object):
    
    
    def __init__(self, df_final):
        self.df_final = df_final
    
    # most raises
    def get_raise_rate(self, df_final):
        
        '''
        Takes df_final and returns "raise_df" with percentual raise rate per player
    
        Parameters
        ----------
        df_final : TYPE
            DESCRIPTION.
    
        Returns
        -------
        raise_df : TYPE
            DESCRIPTION.
    
        '''
        self.df_final = df_final
        games_by_players = self.df_final[self.df_final['action'] == 'INHAND_PLAYER'].groupby(['player']).count()
        most_raises = self.df_final[self.df_final['action'] == 'RAISE'].groupby(['player']).count()
        most_relative_raises = most_raises# / games_by_players
        
        df_raise = pd.DataFrame(index = games_by_players.index, columns = ['games_played', 'raises'])
        df_raise['games_played'] = games_by_players['game_number']
        df_raise['raises'] = most_relative_raises['game_number']
        
        return df_raise

    def plot_raise_rate(self, df_raise):
        
        self.df_raise = df_raise
        
        
        xlabels = self.df_raise.index.tolist() # the label names for the xaxis
        barwidth = 0.35 # the width of the bars
        x = np.arange(len(self.df_raise.index)) # the label locations
        
        fig, ax = plt.subplots(figsize=(16, 9))        
        ax.bar(x-barwidth/2, self.df_raise['games_played'], barwidth, label = 'games')
        ax.bar(x+barwidth/2, self.df_raise['raises'], barwidth, label = 'raises')
        ax.set_xticks(x)
        ax.set_xticklabels(xlabels)
        
        plt.xticks(rotation = 45)
        plt.legend(loc = 'best')
        plt.ylabel('Number of games played / raises')
    
        return fig           

#%%
def get_played_games(df_final):
    played_games = df_final.groupby('game').nunique()['game_number']
    played_games = pd.DataFrame(played_games.rename('game_played'))
    total_games = played_games.sum()
    played_games['percentage'] = (played_games/total_games*100).round(2)
    
    return played_games
    
    
