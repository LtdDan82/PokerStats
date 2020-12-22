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

class GameStats(object):
        
    def __init__(self, df_final):
        
        '''
        Init class with df_final

        Parameters
        ----------
        df_final : dataframe
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        self.df_final = df_final

    def get_played_games(self):
        '''
        Returns percentual games per game
    
        Parameters
        ----------
        df_final : dataframe
            DESCRIPTION.
    
        Returns
        -------
        played_games : dataframe
            DESCRIPTION.
    
        '''
        played_games = self.df_final.groupby('game').nunique()['game_number']
        played_games = pd.DataFrame(played_games.rename('games_played'))
        total_games = played_games.sum()
        played_games['percentage'] = (played_games/total_games*100).round(2)
        played_games['games_played'].astype(int)
        
        return played_games

    def plot_played_games(self):
        
        played_games = self.get_played_games()
        
        labels = played_games.index.tolist()
        sizes = played_games['percentage']
        
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels = labels, autopct='%1.1f%%', shadow = True, startangle=90)
        ax1.axis('equal')
        
        return fig1

    def get_pot_stats(self):
        '''
        Returns mean, median, min, max values for "WIN_POT" grouped by game
    
        Parameters
        ----------
        df_final : dataframe
            DESCRIPTION.
    
        Returns
        -------
        game_potsizes : dataframe
            DESCRIPTION.
    
        '''    
        mean_pot = self.df_final[self.df_final['action'] == 'WIN_POT'].groupby('game')['chips'].mean()
        mean_pot.name = 'mean_pot'
        median_pot = self.df_final[self.df_final['action'] == 'WIN_POT'].groupby('game')['chips'].median()
        median_pot.name = 'median_pot'
        max_pot = self.df_final[self.df_final['action'] == 'WIN_POT'].groupby('game')['chips'].max()
        max_pot.name = 'max_pot'
        min_pot = self.df_final[self.df_final['action'] == 'WIN_POT'].groupby('game')['chips'].min()
        min_pot.name = 'min_pot'
        
        game_potsizes = pd.concat([mean_pot, median_pot, max_pot, min_pot], axis = 1)
        
        return game_potsizes

    def get_gameStats(self, *args):
        '''
        Takes N *args dataframes with gametype as index and  joins them on the index
    
        Parameters
        ----------
        *args : dataframe(s)
            DESCRIPTION.
    
        Returns
        -------
        game_stats : dataframe
            DESCRIPTION.
    
        '''
        self.args = args
        game_stats = pd.concat([*args], axis = 1)
        game_stats = game_stats.round(4)
        
        
        return game_stats



    