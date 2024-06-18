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
    std = dataframe[col].std()
    return std

def mu(dataframe: pd.DataFrame, col: str) -> float:
    mu1 = dataframe[col].mean()
    return mu1

def annualized_vol(std: float) -> float:
    ann_vol = std * (np.sqrt(252))
    return ann_vol

def sharpe_ratio(cagr: float, annualized_vol: float) -> float:
    sharpe = cagr/annualized_vol
    return sharpe

def sortino_ratio():
    pass

def beta(stock_ret: float, ind_ret: float) -> float:
    bet_a = np.cov(stock_ret, ind_ret)
    return bet_a

def treynor_ratio(cagr: float, beta: float) -> float:
    tr = cagr/beta
    return tr

def alpha(cagr: float, mkt_ret: float) -> float:
    re = cagr - mkt_ret
    return re
    
def required_return(beta: float, mkt_ret: float) -> float:
    al = beta * mkt_ret
    return al

def jenson_alpha(cagr: float, required: float) -> float:
    je = cagr - required
    return je

def drawdown(data: pd.DataFrame, col: str) -> pd.Series:
    drawdown = data[col]/data[col].cummax()
    return drawdown

def max_drawdown(drawdown: pd.Series) -> float:
    md = drawdown

def avg_drawdown():
    pass