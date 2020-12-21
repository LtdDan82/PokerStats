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
class PlayerStats(object):
    
    
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
        
    def __get_pfraise_chance(self):
        '''
        Returns the absolute number of pre-flop opportunities where a player
        could raise, re-raise, fold or call
    
        Returns
        -------
        all_chances : series
            DESCRIPTION.
    
        '''
        pre_phase = self.df_final[(self.df_final['gamephase'] == 'pre-flop') |\
                                  (self.df_final['gamephase'] == 'pre swap')]
        # Calculate number of chances to raise / re-raise on preflop
        call_fold_raise = pre_phase[(pre_phase['action'] == 'CALLS') |\
                                    (pre_phase['action'] == 'RAISE') |\
                                        (pre_phase['action'] == 'FOLD') |\
                                            (pre_phase['action'] == 'BET')
                                            ]
        game_number = call_fold_raise.groupby('game_number')['player']\
                                        .agg(list).explode()
        dummy_df = pd.get_dummies(game_number)
        all_chances = dummy_df.sum()
        all_chances.name = 'chance_to_raise'
        
        return all_chances
    
    def get_ListOfPlayers(self):
        
        '''
        Returns unique players

        Returns
        -------
        TYPE np.array
            DESCRIPTION.

        '''
        
        return self.df_final['player'].unique()
    
    def get_wins(self):
    
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
        df_wins = self.df_final[self.df_final['action'] == 'WIN_POT'].groupby('player').count()['game_number']
        df_wins.name = 'won_pot'
   # wins = df_wins.loc[selection]
    
        return df_wins
    
    def get_played_games(self):
        '''
        Returns total and percentual games per game
    
        Parameters
        ----------
        df_final : dataframe
            DESCRIPTION.
    
        Returns
        -------
        played_games : series
            DESCRIPTION.
    
        '''
        games_by_players = self.df_final[self.df_final['action'] == 'INHAND_PLAYER'].groupby(['player']).count()['game_number']
        games_by_players.name = "played_games"
    
        return games_by_players

    def get_vpip_rate(self):
        '''
        Returns the Voluntarily Put In Pot (VPIP) rate for each player
        
        VPIP = (total number of RAISE; CALL; BET events pre-flop/pre-swap)/ games played
        - if a player calls first and then calls a reraise, this is counted as one action

        Returns
        -------
        vpip : series
            DESCRIPTION.

        '''
     
        pre_phase = self.df_final[(self.df_final['gamephase'] == 'pre-flop') |\
                                  (self.df_final['gamephase'] == 'pre swap')]
        call_raise_bet = pre_phase[(pre_phase['action'] == 'CALLS') |\
                                   (pre_phase['action'] == 'RAISE') |\
                                       (pre_phase['action'] == 'BET')]
        # Remove duplicate player names within a game -_> returns a list
        # use .explode method to convert list into row entry
        #Reason: Otherwise we would count the events RAISE; CALL; BET twisce
        game_number = call_raise_bet.groupby('game_number')['player'].unique()\
                        .explode()
        # get dummies for each
        dummy_df = pd.get_dummies(game_number)
        vpip = dummy_df.sum()/self.get_played_games() * 100
        vpip.name = 'VPIP [%]'
                
        return vpip
   
   
    def get_pfr_rate(self):
        '''
        Returns the PREFLOP RAISE RATE (PFR) per player
        
        PFR tracks the percentage of hands in which a particular player makes 
        a preflop raise when having the opportunity to fold or call instead. 
        Note: This includes reraises.
        

        Returns
        -------
        pfr_rate : series
            DESCRIPTION.

        '''
        pre_phase = self.df_final[(self.df_final['gamephase'] == 'pre-flop') |\
                                  (self.df_final['gamephase'] == 'pre swap')]
        raised = pre_phase[pre_phase['action'] == 'RAISE']
        
        game_number = raised.groupby('game_number')['player'].unique().explode()
        dummy_df = pd.get_dummies(game_number)
        pfr_rate = dummy_df.sum()/self.__get_pfraise_chance() * 100
        pfr_rate.name = 'PFR [%]'
        
        return pfr_rate
    
    def get_rfi(self):
        '''
        Returns the RAISE FIRST IN RATE (RFI) per player
        
        RFR tracks the percentage of raises when a player has the opportunity 
        to be the first raiser
        Reraises are excluded

        Returns
        -------
        rfi : series
            DESCRIPTION.

        '''
        pre_phase = self.df_final[(self.df_final['gamephase'] == 'pre-flop') |\
                                  (self.df_final['gamephase'] == 'pre swap')]
        # Get all relevant actions to identify an initial raiser
        first_raised = pre_phase[(pre_phase['action'] == 'RAISE') |\
                                 #(pre_phase['action'] == 'POST_BLIND') |\
                                     (pre_phase['action'] == 'FOLD') |\
                                         (pre_phase['action'] == 'CALLS')]            
        
        # groupby game number and player and aggregate as list    
        game_number = first_raised.groupby(['game_number'])[['action', 'player']].agg(list)        
        unique_game_number = list(set(game_number.index.tolist()))
        
        # collect check_df in all_df        
        all_df = []
        for num in unique_game_number:
            check_df = first_raised[first_raised['game_number'] == num].reset_index(drop=True)
            
            # Select games where a raise occured preflop
            if 'RAISE' in check_df['action'].values:
                ur_row = check_df.loc[check_df['action']=='RAISE'].index.tolist()                
                # drop columns after the first Raise occured
                check_df = check_df.iloc[:ur_row[0]+1, :]               
                # all players including the first raiser had the chance to raise
                check_df['hadChancetoRaise'] = True
            
                # Find players that had a chance to raise and did it
                check_df['didRaise'] = True
                check_df['didRaise'] = check_df['action'].apply(
                                        lambda x: True if x == 'RAISE' else False)
                all_df.append(check_df)
            # Games that had no preflop raise
            else:
                check_df['hadChancetoRaise'] = True
                check_df['didRaise'] = False
                all_df.append(check_df)
                
        df_raise_chance = pd.concat(all_df)
        
        player_raise_df = df_raise_chance.groupby('player')\
            [['hadChancetoRaise', 'didRaise']].sum()
        
        rfi = player_raise_df['didRaise']/player_raise_df['hadChancetoRaise'] * 100
        rfi.name = 'RFI [%]'
        
        return rfi
        
    def _player_specific_stats(self, player):
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
        self.player = player                
        player_df = self.df_final[self.df_final['player'] == self.player]
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
    
    def threebet(self):
        
        print('https://www.mypokercoaching.com/poker-statistics-stats/')
        
    def fold_to_threebet(self):
        
        print('https://www.mypokercoaching.com/poker-statistics-stats/')
        
        
        
        
#%%
# def player_specific_stats(df_final, player):
#     '''
#     Returns counts for specific actions like "Raise, Bet, Fold, ..."
#     Returns sum(chips) for specific actions like "Raise, Bet, Fold, ..."

#     Parameters
#     ----------
#     df_final : dataframe
#         DESCRIPTION.
#     player : str
#         DESCRIPTION.

#     Returns
#     -------
#     stats1_df : dataframe
#         DESCRIPTION.

#     '''
#     player_df = df_final[df_final['player'] == player]
#     # Get counts for column "action"
#     act_count = player_df.groupby('action').count()['game_number']
#     feat_counts = ['ADD_CHIPS', 'BET', 'RAISE', 'CHECKS', 'FOLD', 'CALLS', 'WIN_POT']
#     act_count = act_count.loc[feat_counts]
#     act_count.name = 'count(action)'
    
#     # Get sums for actions
#     act_sums = player_df.groupby('action').sum()['chips']
#     feat_sums = ['ADD_CHIPS', 'BET', 'CALLS', 'CHIPS_RETURNED', 'POST_BLIND', 'RAISE', 'WIN_POT']
#     act_sums = act_sums.loc[feat_sums]
#     act_sums.name = 'sum(chips)'
    
#     #Generate final dataframe by concatenating
#     stats1_df = pd.concat([act_count, act_sums], axis = 1)
    
#     return stats1_df
        
    
    
    
    
    

