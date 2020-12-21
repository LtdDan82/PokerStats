# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 14:19:45 2020

@author: LtdDan82
@github: https://github.com/LtdDan82
"""

import pandas as pd
import numpy as np
import re


from lib.parse_json import parse_events, parse_data
#%%
def get_playerID(df_final, parsed_ids):
    '''
    Function: Extract player_id from multi columns and append to column "players"
    - search for regex pattern in df_final,
    - if True return the pattern, else insert NaN
    - combine columns with regex pattern into one column and append to final_df

    Parameters
    ----------
    df_final : pd.DataFrame
        DESCRIPTION.

    Returns
    -------
    df_final : pd.DataFrame
        DESCRIPTION.

    '''
    # Regex pattern
    regex =  r"^[\dA-Za-z-]{9}[\dA-Za-z-]{5}[\dA-Za-z-]{5}[\dA-Za-z-]{5}[\dA-Za-z]{12}"
    subset = df_final.loc[:,['param_0', 'param_1', 'param_2', 'param_3']].astype(str)
    r = re.compile(regex)
    # Define dataframe to save the player_names
    player_df = pd.DataFrame(columns = ['player'], index = range(subset.shape[0]))
    # check where regex matches in subset
    for col in subset.columns:        
        is_player = subset[col].apply(lambda x: bool(r.match(x)))
        player_vals = subset[col][is_player]
        player_df['player'] = player_df['player'].combine_first(player_vals)
    
    #append to df_final
    df_final['player'] = player_df
    df_final = df_final.replace({"player": parsed_ids})
    return df_final
#%%
def get_playerMoney(df_final):
    '''
    Takes df_final and extracts information on chips depending on the action
    performed.
    Applies information into column df_final['chips']
    

    Parameters
    ----------
    df_final : dataframe
        DESCRIPTION.

    Returns
    -------
    df_final : TYPE
        DESCRIPTION.

    '''
    
    # get subset of relevant parameters
    subset = df_final[['param_0', 'param_1', 'param_2', 'param_3']]
    # convert to numeric, insert nan for non-numeric
    subset = subset.apply(pd.to_numeric, errors = 'coerce')
    # concat with "action" column
    subset = pd.concat([df_final['action'], subset], axis = 1)
    
    
    # Mapping Dictionary: key: column where "money info" is present
    #                       value: list of possible actions
    chips_dict = {'param_0': ['CHIPS_RETURNED', 'POT_SIZE'],
                  'param_1': ['ADD_CHIPS',
                              'POST_BLIND', 'WIN_POT',
                              'RAISE', 'CALLS', 'START_PHASE',
                              'BET'],
                  'param_3': ['INHAND_PLAYER']
                  }
    
    collect_df = pd.DataFrame(index = df_final.index, columns = ['chips'])
    for key in chips_dict:
        chips = subset.loc[subset['action'].isin(chips_dict[key]), key]
        collect_df['chips'] = collect_df['chips'].combine_first(chips)
    
    df_final['chips'] = pd.to_numeric(collect_df['chips'], errors = 'coerce')
    
    return df_final


#%%
def get_gamephase(df_final):
    df_final['gamephase'] = df_final[df_final['action'] == "START_PHASE"]['param_0']
    # backfill the columns
    df_final['gamephase'] = df_final['gamephase'].fillna(method = 'ffill')
    df_final['gamephase'] = df_final['gamephase'].fillna(method = 'bfill')
    return df_final
    
#%%
def extract_transform():
    '''
    -Takes nested function "parse_data" to load the game data
    -extracts playerID and playerMoney from the data
    -removes unnecessary columns

    Returns
    -------
    df_final : dataframe
        DESCRIPTION.

    '''
   
    
   # event_map = parse_events()
    df_final, parsed_ids = parse_data()
    df_final = get_playerID(df_final, parsed_ids)
    df_final = get_playerMoney(df_final)
    df_final = get_gamephase(df_final)
    df_final = df_final.drop(columns = ['type', 'params', 'recipient', 'param_0', 'param_1', 'param_2', 'param_3'])
    df_final = df_final[['game_number', 'game', 'gamephase', 'action', 'player', 'chips']]
    
    return df_final














