# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 16:44:37 2020

@author: LtdDan82
@github: https://github.com/LtdDan82
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
def get_wins(df_final):
    '''
    Returns Number of wins per player.

    Parameters
    ----------
    df_final : dataframe
        DESCRIPTION.

    Returns
    -------
    df_wins : dataframe
        DESCRIPTION.

    '''
    df_wins = df_final[df_final['action'] == 'WIN_POT'].groupby('player').count()['game_number']
    df_wins.name = 'won_pot'
   # wins = df_wins.loc[selection]
    
    return df_wins

#%%
# most raises
def get_raise_rate(df_final):
    
    '''
    Takes df_final and returns "raise_df" with number of raises per player

    Parameters
    ----------
    df_final : TYPE
        DESCRIPTION.

    Returns
    -------
    raise_df : TYPE
        DESCRIPTION.

    '''
    games_by_players = df_final[df_final['action'] == 'INHAND_PLAYER'].groupby(['player']).count()
    most_raises = df_final[df_final['action'] == 'RAISE'].groupby(['player']).count()
    
    df_raise = pd.DataFrame(index = games_by_players.index, columns = ['games_played', 'total_raises'])
    df_raise['games_played'] = games_by_players['game_number']
    df_raise['total_raises'] = most_raises['game_number']
    
    return df_raise

#%%   
def get_phase_raises(df_final, phase):
    '''
    - Takes df_final and searches for raises in phase 
    - args for phase: 'preflop', 'flop', 'turn', 'river'
    - For drawing games 'preflop' = 'pre swap', 'flop' = 'first swap', 
    is automatically mapped

    Parameters
    ----------
    df_final : TYPE
        DESCRIPTION.
    phase : TYPE, optional
        DESCRIPTION. The default is 'pre-flop'.

    Returns
    -------
    None.

    '''
    if phase == 'preflop':
        get_phase = ('pre-flop', 'pre swap')
    elif phase == 'flop':    
        get_phase = ('flop', 'first swap' )
    elif phase == 'turn': 
        get_phase = ('turn, second swap')
    elif phase == 'river':
        get_phase = ('river', 'third swap')
    else:
        raise AttributeError('Unknow argument for "phase", please check function docstring')
    
    df_raise_event = df_final[((df_final['gamephase'] == get_phase[0]) | (df_final['gamephase'] == get_phase[1])) & (df_final['action'] == 'RAISE')]
    df = df_raise_event[df_raise_event['action'] == 'RAISE'].groupby(['player']).count()
    raise_events = pd.DataFrame(index = df.index, columns = [get_phase[0] + '_raises'])
    raise_events[get_phase[0] + '_raises'] = df['game_number']
    #raise_events['raised_phase'] = get_phase[0]
    
    return raise_events
#%%
def sum_player_stats(df_final):
    '''
    Returns total_games, wins, total_raises, preflop_raises per player
    Nested Functions:
        get_wins, get_phase_raises

    Parameters
    ----------
    df_final : dataframe
        DESCRIPTION.

    Returns
    -------
    df_player_stats : dataframe
        DESCRIPTION.

    '''
    #get wins    
    df_wins = get_wins(df_final)
    # get total_raises    
    sum_stats = [get_raise_rate(df_final)]
    #get raises in phase = []
    for phase in ['preflop']:
        sum_stats.append(get_phase_raises(df_final, phase))
    sum_stats.append(df_wins)
    
    df_player_stats = pd.concat(sum_stats, axis = 1)
    
    return df_player_stats

#%%
def plot_player_stats(df_player_stats):
    '''
    Plots total_games, wins, total_raises, preflop_raises per player as barplot
    Return matplotlib.figure object

    Parameters
    ----------
    df_player_stats : dataframe
        DESCRIPTION.

    Returns
    -------
    fig : matplotlib.figure.Figure
        DESCRIPTION.

    '''
    xlabels = df_player_stats.index.tolist() # the label names for the xaxis
    barwidth = 0.1 # the width of the bars
    x = np.arange(len(df_player_stats.index)) # the label locations
    #Generate fig, ax object
    fig, ax = plt.subplots(figsize=(16, 9))


    #Bar - Played Games       
    bars2 = ax.bar(x-2*barwidth, df_player_stats['games_played'], barwidth, label = 'played_games')
    for rect in bars2:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')
        
    #Bar - Won Pot        
    bars4 = ax.bar(x-1*barwidth, df_player_stats['won_pot'], barwidth, label = 'won_pot')
    for rect in bars4:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')
        
    #Bar - Total Raises
    bars = ax.bar(x+1*barwidth, df_player_stats['total_raises'], barwidth, label = 'total_raises')
    for rect in bars:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')
    
    # Bar - Preflop Raises    
    bars3 = ax.bar(x+2*barwidth, df_player_stats['pre-flop_raises'], barwidth, label = 'pre-flop_raises')
    for rect in bars3:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height, '%d' % int(height), ha='center', va='bottom')

    ax.set_xticks(x)
    ax.set_xticklabels(xlabels)

    plt.xticks(rotation = 45)
    plt.legend(loc = 'best')
    plt.ylabel('Number of games played/won pot/raises')
    
    return fig           


    
    
