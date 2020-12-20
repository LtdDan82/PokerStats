# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

#%%

df_final = extract_transform()
#%%
def player_vs_opp(df_final, player, opp):
    # dataframe machen mit player und gegner (als liste) und dann

    if not isinstance(player, str):
        raise TypeError('function argument "player" = ' + str(player.__repr__()) + ' is not a string')
        
    elif not isinstance(opp, list):
        raise TypeError('function argument "*opp" = ' + str(opp.__repr__()) + ' is not a list')
    
    search = [player] + opp
    
    df = df_final[df_final['player'].isin(search)]
    
    game_df = df.groupby(['game_number', 'player', 'action']).sum()
    game_winner = game_df[game_df.loc['action',:] == 'WIN_POT']
    
    return search
#%%
def player_specific_stats(df_final, player):
    '''
    Returns counts for specific actions like "Raise, Bet, Fold, ..."
    Returns sum(chips) for specific actions like "Raise, Bet, Fold, ..."

    Parameters
    ----------
    df_final : dataframe
        DESCRIPTION.
    player : str
        DESCRIPTION.

    Returns
    -------
    stats1_df : dataframe
        DESCRIPTION.

    '''
    player_df = df_final[df_final['player'] == player]
    # Get counts for column "action"
    act_count = player_df.groupby('action').count()['game_number']
    feat_counts = ['ADD_CHIPS', 'BET', 'RAISE', 'CHECKS', 'FOLD', 'CALLS', 'WIN_POT']
    act_count = act_count.loc[feat_counts]
    act_count.name = 'count(action)'
    
    # Get sums for actions
    act_sums = player_df.groupby('action').sum()['chips']
    feat_sums = ['ADD_CHIPS', 'BET', 'CALLS', 'CHIPS_RETURNED', 'POST_BLIND', 'RAISE', 'WIN_POT']
    act_sums = act_sums.loc[feat_sums]
    act_sums.name = 'sum(chips)'
    
    #Generate final dataframe by concatenating
    stats1_df = pd.concat([act_count, act_sums], axis = 1)
    
    return stats1_df
    
    

