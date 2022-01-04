import unittest
from itertools import groupby

import pandas as pd
import numpy as np



class MyTestCase(unittest.TestCase):

    df = pd.read_csv("Dogs_short.csv", parse_dates=[["Date","Time"]], dayfirst=True)
    df.drop(df.index[df.SP.eq(0)], inplace=True)

    df["Fin"] = df["Fin"].where(df["Fin"].eq("1"), 0).astype(int)
    df.sort_values(by="Date_Time", inplace=True)
    df["Date_Time_dt"] = df["Date_Time"].dt.date
    df = df.drop_duplicates(subset=["Dog name", "Date_Time_dt"])
    df.reset_index(inplace=True, drop=True)

    # 1-task
    #@unittest.skip("demonstrating skipping")
    def test_convo_group_mean(self):
        cmg = convo_mean_group(self.df, "SP", 5, "Dog name")
        normal_rolling = self.df.groupby(by="Dog name")["SP"].rolling(5, min_periods=1).mean()
        normal_rolling.sort_index(level=1, inplace=True)
        normal_rolling.index = normal_rolling.index.droplevel(0)
        cmg.name = normal_rolling.name
        pd.testing.assert_series_equal(cmg, normal_rolling)

    # 2-task
    #@unittest.skip("demonstrating skipping")
    def test_races_since_win(self):
        self.df["since_last_win"] = since_last_win(self.df, "Dog name")
        last_value = self.df.loc[self.df["Dog name"].eq("Foxwood Boom"), "Fin"][::-1].cumsum().eq(0).sum() - 1
        self.assertEqual(last_value, self.df.loc[self.df["Dog name"].eq("Foxwood Boom"), "since_last_win"].iloc[-1])

    # 3-task
    #@unittest.skip("demonstrating skipping")
    def test_insert_historical(self):
        c = self.df.groupby(by="Dog name")["SP"].transform(lambda x: x.expanding().mean().shift())
        self.df["expanding_SP"] = self.df.groupby(by="Dog name")["SP"].transform(lambda x: x.expanding().mean())
        until_df = self.df.loc[:, ["Dog name", "expanding_SP", "Date_Time"]]
        self.df.drop("expanding_SP", axis=1, inplace=True)
        self.df = insert_historical_attrs_groupby(self.df, until_df, ["Dog name"], ["expanding_SP"])

        pd.testing.assert_series_equal(self.df["expanding_SP"], c, check_names=False)

def since_last_win(df, group_attr):
    return df.groupby(group_attr)["Fin"].transform(lambda x: x.groupby(x.cumsum()).cumcount().shift())

def convo_mean_group(df, attr, window_size, group_attr):
    groups = df.groupby(group_attr)[attr]
    s = [[],[]]
    for i, grp in groups:
        s[1].extend(grp.index)
        c = np.convolve(grp, np.ones(window_size))[:len(grp)]
        divisor = np.ones(len(grp))*window_size
        divisor[:min(len(grp),window_size)] = np.arange(min(len(grp),window_size)) +1
        s[0].extend(c/divisor)
    return pd.Series(s[0], index=s[1]).sort_index()

def insert_historical_attrs_groupby(df, historical_df, merge_variables, new_variables):
    interim_df = df.groupby(merge_variables + [df["Date_Time"].dt.normalize()]).size()
    interim_df = interim_df.reset_index().iloc[:, :-1]

    interim_df_hist = historical_df.groupby(merge_variables + [df["Date_Time"].dt.normalize()])[new_variables].last().reset_index()

    interim_df = interim_df.merge(interim_df_hist, on=merge_variables, suffixes=(None, "_hist"))
    interim_df = interim_df.loc[interim_df["Date_Time"].gt(interim_df["Date_Time_hist"]),:].drop_duplicates(keep="last", subset=merge_variables + ["Date_Time"])

    return df.merge(interim_df, how="left", left_on=merge_variables + [df["Date_Time"].dt.normalize()], right_on= merge_variables + ["Date_Time"])


if __name__ == '__main__':
    unittest.main()
