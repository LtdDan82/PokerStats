# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from lib.data_transform import extract_transform

plt.style.use("ggplot")
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = "Ubuntu"
plt.rcParams["font.monospace"] = "Ubuntu Mono"
plt.rcParams["font.size"] = 12
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["legend.fontsize"] = 12
plt.rcParams["figure.titlesize"] = 14

# %%
# datestring = '12122020'
# df_final = extract_transform(datestring)


#%%
class PlayerStats(object):
    def __init__(self, df_final):

        """
        Init class with df_final

        Parameters
        ----------
        df_final : dataframe
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.df_final = df_final

    def __get_pfraise_chance(self):
        """
        Returns the absolute number of pre-flop opportunities where a player
        could raise, re-raise, fold or call

        Returns
        -------
        all_chances : series
            DESCRIPTION.

        """
        pre_phase = self.df_final[
            (self.df_final["gamephase"] == "pre-flop")
            | (self.df_final["gamephase"] == "pre swap")
        ]
        # Calculate number of chances to raise / re-raise on preflop
        call_fold_raise = pre_phase[
            (pre_phase["action"] == "CALLS")
            | (pre_phase["action"] == "RAISE")
            | (pre_phase["action"] == "FOLD")
            | (pre_phase["action"] == "BET")
        ]
        game_number = (
            call_fold_raise.groupby("game_number")["player"].agg(list).explode()
        )
        dummy_df = pd.get_dummies(game_number)
        all_chances = dummy_df.sum()
        all_chances.name = "chance_to_raise"

        return all_chances

    def get_ListOfPlayers(self):

        """
        Returns unique players

        Returns
        -------
        TYPE np.array
            DESCRIPTION.

        """

        players = self.df_final["player"].dropna().unique()
        players = players.tolist()

        return players

    def get_wins(self):

        """
        Returns Number of wins per player.

        Parameters
        ----------
        df_final : dataframe
            DESCRIPTION.

        Returns
        -------
        df_wins : dataframe
            DESCRIPTION.

        """
        df_wins = (
            self.df_final[self.df_final["action"] == "WIN_POT"]
            .groupby("player")
            .count()["game_number"]
        )
        df_wins.name = "won_pot"
        # wins = df_wins.loc[selection]

        return df_wins

    def get_played_games(self):
        """
        Returns total and percentual games per game

        Parameters
        ----------
        df_final : dataframe
            DESCRIPTION.

        Returns
        -------
        played_games : series
            DESCRIPTION.

        """
        games_by_players = (
            self.df_final[self.df_final["action"] == "INHAND_PLAYER"]
            .groupby(["player"])
            .count()["game_number"]
        )
        games_by_players.name = "played_games"

        return games_by_players

    def get_phase_raises(self, phase):
        """
        - Takes df_final and searches for raises in phase
        - args for phase: 'preflop', 'flop', 'turn', 'river',
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

        """
        self.phase = phase

        if self.phase == "preflop":
            get_phase = ("pre-flop", "pre swap")
        elif self.phase == "flop":
            get_phase = ("flop", "first swap")
        elif self.phase == "turn":
            get_phase = "turn, second swap"
        elif self.phase == "river":
            get_phase = ("river", "third swap")
        else:
            raise AttributeError(
                'Unknow argument for "phase", please check function docstring'
            )

        df_raise_event = self.df_final[
            (
                (self.df_final["gamephase"] == get_phase[0])
                | (self.df_final["gamephase"] == get_phase[1])
            )
            & (self.df_final["action"] == "RAISE")
        ]
        df = (
            df_raise_event[df_raise_event["action"] == "RAISE"]
            .groupby(["player"])
            .count()
        )
        raise_events = pd.DataFrame(index=df.index, columns=[get_phase[0] + "_raises"])
        raise_events[get_phase[0] + "_raises"] = df["game_number"]

        return raise_events

    def get_raise_rate(self):

        """
        Takes df_final and returns "df_raise" with number of raises per player

        Parameters
        ----------
        df_final : TYPE
            DESCRIPTION.

        Returns
        -------
        raise_df : TYPE
            DESCRIPTION.

        """
        games_by_players = (
            self.df_final[self.df_final["action"] == "INHAND_PLAYER"]
            .groupby(["player"])
            .count()
        )
        most_raises = (
            self.df_final[self.df_final["action"] == "RAISE"]
            .groupby(["player"])
            .count()
        )

        df_raise = pd.DataFrame(
            index=games_by_players.index, columns=["games_played", "total_raises"]
        )
        df_raise["games_played"] = games_by_players["game_number"]
        df_raise["total_raises"] = most_raises["game_number"]

        return df_raise

    def sum_player_stats(self):
        """
        Returns total_games, wins, total_raises, preflop_raises (includes reraise) per player
        Nested class methods:
            get_wins, get_phase_raises, get_raise_rate

        Parameters
        ----------
        df_final : dataframe
            DESCRIPTION.

        Returns
        -------
        df_player_stats : dataframe
            DESCRIPTION.

        """
        # get wins
        df_wins = self.get_wins()
        # get total_raises
        sum_stats = [self.get_raise_rate()]
        # get raises in phase = []
        for phase in ["preflop"]:
            sum_stats.append(self.get_phase_raises(phase))
        sum_stats.append(df_wins)

        df_player_stats = pd.concat(sum_stats, axis=1)

        return df_player_stats

    def plot_player_stats(self):
        """
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

        """

        df_player_stats = self.sum_player_stats()

        xlabels = df_player_stats.index.tolist()  # the label names for the xaxis
        barwidth = 0.1  # the width of the bars
        x = np.arange(len(df_player_stats.index))  # the label locations
        # Generate fig, ax object
        fig, ax = plt.subplots(figsize=(16, 9))

        # Bar - Played Games
        bars2 = ax.bar(
            x - 2 * barwidth,
            df_player_stats["games_played"],
            barwidth,
            label="played_games",
        )
        for rect in bars2:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                height,
                "%d" % int(height),
                ha="center",
                va="bottom",
            )

        # Bar - Won Pot
        bars4 = ax.bar(
            x - 1 * barwidth, df_player_stats["won_pot"], barwidth, label="won_pot"
        )
        for rect in bars4:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                height,
                "%d" % int(height),
                ha="center",
                va="bottom",
            )

        # Bar - Total Raises
        bars = ax.bar(
            x + 1 * barwidth,
            df_player_stats["total_raises"],
            barwidth,
            label="total_raises",
        )
        for rect in bars:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                height,
                "%d" % int(height),
                ha="center",
                va="bottom",
            )

        # Bar - Preflop Raises
        bars3 = ax.bar(
            x + 2 * barwidth,
            df_player_stats["pre-flop_raises"],
            barwidth,
            label="pre-flop_raises",
        )
        for rect in bars3:
            height = rect.get_height()
            plt.text(
                rect.get_x() + rect.get_width() / 2.0,
                height,
                "%d" % int(height),
                ha="center",
                va="bottom",
            )

        ax.set_xticks(x)
        ax.set_xticklabels(xlabels)

        plt.xticks(rotation=45)
        plt.legend(loc="best")
        plt.ylabel("Number of games played/won pot/raises")

        return fig

    def _player_specific_stats(self, player):
        """
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

        """
        self.player = player
        player_df = self.df_final[self.df_final["player"] == self.player]
        # Get counts for column "action"
        act_count = player_df.groupby("action").count()["game_number"]
        feat_counts = ["BET", "RAISE", "CHECKS", "FOLD", "CALLS", "WIN_POT"]
        act_count = act_count.loc[feat_counts]
        act_count.name = "count(action)"

        # Get sums for actions
        act_sums = player_df.groupby("action").sum()["chips"]
        feat_sums = ["BET", "RAISE", "CHECKS", "FOLD", "CALLS", "WIN_POT"]
        act_sums = act_sums.loc[feat_sums]
        act_sums.name = "sum(chips)"

        # Generate final dataframe by concatenating
        stats1_df = pd.concat([act_count, act_sums], axis=1)

        return stats1_df

    def get_vpip_rate(self):
        """
        Returns the Voluntarily Put In Pot (VPIP) rate for each player

        VPIP = (total number of RAISE; CALL; BET events pre-flop/pre-swap)/ games played
        - if a player calls first and then calls a reraise, this is counted as one action

        Returns
        -------
        vpip : series
            DESCRIPTION.

        """

        pre_phase = self.df_final[
            (self.df_final["gamephase"] == "pre-flop")
            | (self.df_final["gamephase"] == "pre swap")
        ]
        call_raise_bet = pre_phase[
            (pre_phase["action"] == "CALLS")
            | (pre_phase["action"] == "RAISE")
            | (pre_phase["action"] == "BET")
        ]
        # Remove duplicate player names within a game -_> returns a list
        # use .explode method to convert list into row entry
        # Reason: Otherwise we would count the events RAISE; CALL; BET twisce
        game_number = call_raise_bet.groupby("game_number")["player"].unique().explode()
        # get dummies for each
        dummy_df = pd.get_dummies(game_number)
        vpip = dummy_df.sum() / self.get_played_games() * 100

        vpip.name = "VPIP [%]"

        return vpip

    def get_pfr_rate(self):
        """
        Returns the PREFLOP RAISE RATE (PFR) per player

        PFR tracks the percentage of hands in which a particular player makes
        a preflop raise when having the opportunity to fold or call instead.
        Note: This includes reraises.


        Returns
        -------
        pfr_rate : series
            DESCRIPTION.

        """
        pre_phase = self.df_final[
            (self.df_final["gamephase"] == "pre-flop")
            | (self.df_final["gamephase"] == "pre swap")
        ]
        raised = pre_phase[pre_phase["action"] == "RAISE"]

        game_number = raised.groupby("game_number")["player"].unique().explode()
        dummy_df = pd.get_dummies(game_number)
        pfr_rate = dummy_df.sum() / self.__get_pfraise_chance() * 100
        pfr_rate.name = "PFR [%]"

        return pfr_rate

    def get_rfi_rate(self):
        """
        Returns the RAISE FIRST IN RATE (RFI) per player

        RFR tracks the percentage of raises when a player has the opportunity
        to be the first raiser
        Reraises are excluded

        Returns
        -------
        rfi : series
            DESCRIPTION.

        """
        pre_phase = self.df_final[
            (self.df_final["gamephase"] == "pre-flop")
            | (self.df_final["gamephase"] == "pre swap")
        ]
        # Get all relevant actions to identify an initial raiser
        first_raised = pre_phase[
            (pre_phase["action"] == "RAISE")
            | (  # (pre_phase['action'] == 'POST_BLIND') |\
                pre_phase["action"] == "FOLD"
            )
            | (pre_phase["action"] == "CALLS")
        ]

        # groupby game number and player and aggregate as list
        game_number = first_raised.groupby(["game_number"])[["action", "player"]].agg(
            list
        )
        unique_game_number = list(set(game_number.index.tolist()))

        # collect check_df in all_df
        all_df = []
        for num in unique_game_number:
            check_df = first_raised[first_raised["game_number"] == num].reset_index(
                drop=True
            )

            # Select games where a raise occured preflop
            if "RAISE" in check_df["action"].values:
                ur_row = check_df.loc[check_df["action"] == "RAISE"].index.tolist()
                # drop columns after the first Raise occured
                check_df = check_df.iloc[: ur_row[0] + 1, :]
                # all players including the first raiser had the chance to raise
                check_df["hadChancetoRaise"] = True

                # Find players that had a chance to raise and did it
                check_df["didRaise"] = True
                check_df["didRaise"] = check_df["action"].apply(
                    lambda x: True if x == "RAISE" else False
                )
                all_df.append(check_df)
            # Games that had no preflop raise
            else:
                check_df["hadChancetoRaise"] = True
                check_df["didRaise"] = False
                all_df.append(check_df)

        df_raise_chance = pd.concat(all_df)

        player_raise_df = df_raise_chance.groupby("player")[
            ["hadChancetoRaise", "didRaise"]
        ].sum()

        rfi = player_raise_df["didRaise"] / player_raise_df["hadChancetoRaise"] * 100
        rfi.name = "RFI [%]"

        return rfi

    def cbet_flop(self):
        pre_phase = self.df_final[
            (self.df_final["gamephase"] == "pre-flop")
            | (self.df_final["gamephase"] == "pre swap")
            | (self.df_final["gamephase"] == "flop")
            | (self.df_final["gamephase"] == "first swap")
        ]

        raised_cbets = pre_phase[
            (pre_phase["action"] == "RAISE") | (pre_phase["action"] == "BET")
        ]
        game_number = raised_cbets.groupby(["game_number"])[["action", "player"]].agg(
            list
        )
        unique_game_number = list(set(game_number.index.tolist()))
        for num in unique_game_number:
            check_df = raised_cbets[raised_cbets["game_number"] == num].reset_index(
                drop=True
            )
            # todo

    def get_player_action(self):
        actions = self.df_final.query(
            "action in ['RAISE', 'BET', 'CHECKS', 'FOLD', 'CALLS', 'WIN_POT']"
        )
        player_action_count = pd.DataFrame(
            actions.groupby(["player", "action"])["game_number"].count()
        )
        player_action_count = player_action_count.rename(
            columns={"game_number": "counts"}
        )
        df_pivot = pd.pivot_table(
            data=player_action_count,
            index=player_action_count.index.get_level_values("player"),
            columns=player_action_count.index.get_level_values("action"),
        )

        df_pivot.columns = df_pivot.columns.to_flat_index()
        colnames = df_pivot.columns.tolist()
        colnames = [x[1] for x in colnames]
        colnames = [x + " [per_game]" for x in colnames]

        df_pivot.columns = colnames

        df_pivot = df_pivot

        return df_pivot

    def get_cashgame_statistics(self):
        # Voluntarily put into pot
        vpip = self.get_vpip_rate()
        # preflop raise rate
        pfr = self.get_pfr_rate()
        # raise first in rate
        rfi = self.get_rfi_rate()

        count_stats = self.get_player_action().divide(self.get_played_games(), axis=0)

        return pd.concat([vpip, pfr, rfi, count_stats], axis=1)

    # def fold_to_threebet(self):

    #     print('https://www.mypokercoaching.com/poker-statistics-stats/')


#%%
