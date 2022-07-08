# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 10:44:50 2020

@author: LtdDan82
@github: https://github.com/LtdDan82
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#%%


def highlight_max(data, color="lightcoral"):
    """
    function for pd.style.apply()
    highlight the maximum in a Series or DataFrame
    """
    attr = "background-color: {}".format(color)
    # remove % and cast to float
    data = data.replace("%", "", regex=True).astype(float)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else "" for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(
            np.where(is_max, attr, ""), index=data.index, columns=data.columns
        )


def highlight_min(data, color="lightgreen"):
    """
    function for pd.style.apply()
    highlight the minimum in a Series or DataFrame
    """
    attr = "background-color: {}".format(color)
    # remove % and cast to float
    data = data.replace("%", "", regex=True).astype(float)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_min = data == data.min()
        return [attr if v else "" for v in is_min]
    else:  # from .apply(axis=None)
        is_min = data == data.min().min()
        return pd.DataFrame(
            np.where(is_min, attr, ""), index=data.index, columns=data.columns
        )
