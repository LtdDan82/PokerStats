# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 12:18:52 2020

@author: LtdDan82
@github: https://github.com/LtdDan82
"""

import json
import numpy as np
import pandas as pd
import os

# import openpyxl
# %%


def add_game_state(df, event_map):

    game_state = []
    for elem in df["type"]:
        game_state.append(event_map[event_map.index == elem].values[0][0])

    df["action"] = game_state
    return df


# %%
def get_gametype(df, event_map):

    action = df[
        df["type"]
        == event_map[event_map["action"] == "ROUND_STARTED"].index.tolist()[0]
    ]["params"].values[0][0]
    df["game"] = action

    return df


# %%
def fill_list(listitem, maxlen):

    """

    Parameters
    ----------
    listitem : list
        DESCRIPTION.
    maxlen : int
        DESCRIPTION.

    Checks for len(list),
    if smaller than maxlen, append np.nan to reach maxlen
    else keep listitem

    Returns
    -------
    listitem : list
        DESCRIPTION.

    """
    length = len(listitem)
    if length == maxlen:
        listitem = listitem
    elif length < maxlen:
        diff = maxlen - length
        make_add = [np.nan] * diff
        listitem = listitem + make_add

    return listitem


# %%
def parse_events():

    directory = os.getcwd()

    events = os.path.join(directory, "data", "events_map.xlsx")
    # events = 'https://github.com/LtdDan82/PokerStats/blob/master/data/events_map.xlsx'
    event_df = pd.read_excel(
        events, index_col=0, header=None, names=["action"], engine="openpyxl"
    )
    return event_df


# %%
def parse_data(datestring):

    """
    datestring in the form: "ddmmyyyy"

    maxlen = 4 aktuell noch hard gecoded, --> aus Daten ziehen

    Returns
    -------
    df_final : TYPE
        DESCRIPTION.
    parsed_ids : TYPE
        DESCRIPTION.

    """
    assert type(datestring) == str
    directory = os.getcwd()
    session_dir = "session_" + datestring
    history_file = "history_" + datestring + ".txt"
    publicId_file = "publicID_" + datestring + ".txt"
    json_data = os.path.join(directory, "data", session_dir, history_file)
    # json_data = "https://github.com/LtdDan82/PokerStats/blob/master/data/history_12122020.txt"
    pub_ids = os.path.join(directory, "data", session_dir, publicId_file)
    # pub_ids = "./data/public_id.txt"
    # pub_ids = "https://github.com/LtdDan82/PokerStats/blob/master/data/public_id.txt"
    event_map = parse_events()
    with open(json_data, "r") as f1, open(pub_ids, "r") as f2:
        parsed_history = json.load(f1)
        parsed_ids = json.load(f2)
        f1.close()
        f2.close()
        del (f1, f2)

    df_collect = []
    game_num = 0
    for k in range(len(parsed_history)):
        game_num += 1
        game = parsed_history[k]
        df = pd.DataFrame.from_dict(game)
        df = add_game_state(df, event_map)
        df = get_gametype(df, event_map)
        df["params"] = df["params"].apply(lambda x: fill_list(x, maxlen=4))
        df["game_number"] = game_num

        df_collect.append(df)

    df_final = pd.concat(df_collect)

    df_final = df_final.reset_index(drop=True)

    for k in range(4):
        df_final.loc[:, "param_" + str(k)] = df_final.params.map(lambda x: x[k])

    return df_final, parsed_ids


df_final, parsed_ids = parse_data("12122020")
