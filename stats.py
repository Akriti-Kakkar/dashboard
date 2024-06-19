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

def avg_monthly_twr(data: pd.DataFrame, col: str) -> float:
    data1 = pd.DataFrame(data[col])
    data1['Month'] = data1.index.month
    data1['ret1'] = 1+data1[col]
    gp = data1.groupby(by='Month').agg({'ret1': 'prod'})
    gp1 = gp-1
    gp_m1 = gp1.mean()
    gp_m = gp_m1[0]
    return gp_m

def last_n_twr(data: pd.DataFrame, col: str, n: int) -> float:
    slice_ = data.iloc[-n:]
    slice_ret = pd.DataFrame(slice_[col])
    slice_ret['ret1'] = 1+slice_ret[col]
    gp = slice_ret.agg({'ret1':'prod'})
    gp1 = gp-1
    gp_m = gp1[0]
    return gp_m
    
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

def downside_deviation(data: pd.DataFrame, col: str) -> float:
    frame1 = data[data[col]<0]
    frame = frame1[col]
    frame = frame.reset_index(drop=True)
    std = frame.std()
    ann_std = std * (np.sqrt(252))
    return ann_std


def sortino_ratio(ann_ret: float, ann_std: float) -> float:
    sort1 = ann_ret/ann_std
    return sort1

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
    '''
    parse equity curves column and generate a resultant pandas series 
    appended to you dataframe as well as used independently
    '''
    drawdown = (data[col]/data[col].cummax())-1
    return drawdown

def max_drawdown(drawdown: pd.Series) -> float:
    md = drawdown.min()
    return md

def avg_drawdown(drawdown: pd.Series) -> float:
    ad = drawdown.mean()
    return ad

def getMaxLength(arr: pd.Series, input: bool) -> int:
    '''
    enter data['returns'] as arr 
    enter 1 for positive returns, enter 0 for negative returns as input
    result will max cons occurances of the input in arr
    '''
    if input == 1:
        arr1 = pd.Series(np.where(arr >= 0, 1, 0))
    elif input == 0:
        arr1 = pd.Series(np.where(arr < 0, 1, 0))
    
    # initialize count
    count = 0

    # initialize max
    result = 0
    n = len(arr1)
    for i in range(0, n):

        # Reset count when 0 is found
        if (arr1[i] == 0):
            count = 0

        # If 1 is found, increment count
        # and update result if count
        # becomes more.
        else:

            # increase count
            count+= 1
            result = max(result, count)

    return result
