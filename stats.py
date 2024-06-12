from typing import *
import pandas as pd
from datetime import timedelta, date
import numpy as np


def date_range(starting_date: object, ending_date: object, data: pd.DataFrame) -> pd.DataFrame:
    range1 = pd.bdate_range(starting_date, ending_date)
    range2 = pd.DataFrame(index=range1)
    dataframe = pd.merge(range2, data, left_index=True, right_index=True, how='left')
    return dataframe

def duration(starting_date: object, ending_date: object) -> int:
    duration1 = ending_date - starting_date
    days = duration1.days + 1
    weekdays1 = (starting_date+timedelta(x+1) for x in range(days))
    weekdays = sum(1 for day in weekdays1 if day.weekday() < 5)
    return weekdays

def win_days(frame: pd.DataFrame, value: str) -> int:
    win_frame = frame[value].apply(lambda x: 1 if x >= 0 else 0)
    win = win_frame.sum()
    return win
        
def loss_days(frame: pd.DataFrame, value: str) -> int:
    loss_frame = frame[value].apply(lambda x: 1 if x < 0 else 0)
    loss = loss_frame.sum()
    return loss   

def win_pct(win_days: int, duration: int) -> float:
    win_stat = win_days/duration
    return win_stat

def win_loss(win_days: int, loss_days: int) -> float:
    wl = win_days/loss_days
    return wl

def max_cons_pos_days():
    pass

def max_cons_neg_days():
    pass

def cagr(starting_value: float, ending_value: float, duration: int) -> float:
    n = 252/duration
    cagr_ret = ((ending_value/starting_value)**n)-1
    return cagr_ret

def stdev(dataframe: pd.DataFrame, col: str) -> float:
    std = dataframe[col].stdev()
    return std

def annualized_vol(std: float) -> float:
    ann_vol = std * (np.sqrt(252))
    return ann_vol

def sharpe_ratio(cagr: float, annualized_vol: float) -> float:
    sharpe = cagr/annualized_vol
    return sharpe

def sortino_ratio():
    pass

def beta():
    pass

def treynor_ratio():
    pass

def alpha():
    pass

def required_return():
    pass

def max_drawdown():
    pass

def avg_drawdown():
    pass