from typing import *
import pandas as pd
from datetime import timedelta, date
import numpy as np

def color_code(col1, col2=0):
    if col1 >= col2:
        return "green"
    else:
        return "red"
    
def color_code_kwarg(col1):
    if (col1 > 0) | (col1 == 0):
        return "color: green"
    else:
        return "color: red"
    
def color_kwargs(col1):
    if col1.startswith("-") or col1.startswith("("):
        return "color: red"
    else:
        return "color: green"

def comparison(basket_stat, index_stat, nature):
    if basket_stat>index_stat:
        if nature == "normal":
            pf = "Outperformed"
        elif nature == "risk":
            pf = "Riskier"
        elif nature == "performance":
            pf = "Higher Hurdle Rate"
        elif nature == "deposits":
            pf = "Additional Deposits"
    elif basket_stat<index_stat:
        if nature == "normal":
            pf = "Underperformed"
        elif nature == "risk":
            pf = "Less Risky"
        elif nature == "performance":
            pf = "Lower Hurdle Rate"
        elif nature == "deposits":
            pf = "Withdrawals"
    else:
        pf = "Equalled"
    return pf

def comparison_alt(basket_stat, index_stat, nature):
    if basket_stat<index_stat:
        if nature == "normal":
            pf = "Outperformed"
        elif nature == "risk":
            pf = "Riskier"
    elif basket_stat>index_stat:
        if nature == "normal":
            pf = "Underperformed"
        elif nature == "risk":
            pf = "Less Risky"
    else:
        pf = "Equalled"
    return pf

def comparison_emoji(sentiment):
    if sentiment in ("Equalled", "Outperformed", "Higher Hurdle Rate", 
                     "Less Risky", "Additional Deposits"):
        emoji = "👍"
    elif sentiment in ("Underperformed", "Riskier", "Lower Hurdle Rate",
                       "Withdrawals"):
        emoji = "👎"
    return emoji

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
    frame = frame.dropna(subset=[value])
    win_frame = frame[value].apply(lambda x: 1 if x >= 0 else 0)
    win = win_frame.sum()
    return win
        
def loss_days(frame: pd.DataFrame, value: str) -> int:
    frame = frame.dropna(subset=[value])
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

def last_n_twr(data: pd.DataFrame, col: str, n: int, filter: bool) -> float:
    if filter == False:
        slice_ = data.iloc[-n:]
        print(slice_)
        slice_ret = pd.DataFrame(slice_[col])
        slice_ret['ret1'] = 1+slice_ret[col]
        gp = slice_ret.agg({'ret1':'prod'})
        gp1 = gp-1
        gp_m = gp1[0]
    elif filter == True:
        data1 = data.dropna(subset=[col])
        slice_ = data1.iloc[-n:]
        print(slice_)
        slice_ret = pd.DataFrame(slice_[col])
        slice_ret['ret1'] = 1+slice_ret[col]
        gp = slice_ret.agg({'ret1':'prod'})
        gp1 = gp-1
        gp_m = gp1[0]
    return gp_m

def last_n_mwr(wt_cash: pd.Series, change: pd.Series, start_capital_eod: float,
               n=0) -> float:
    if n==0:
        change = change.dropna()
    else:
        change = change.dropna()
        change = change.iloc[-n:]
    print('n days change', change)
    start_cap = start_capital_eod.iloc[0]
    mwr = change.sum() /(start_cap + wt_cash.sum())
    print('MWR', change.sum(), start_cap, wt_cash.sum(), mwr)
    return mwr

def last_n_weighted_cash_flow(data: pd.Series, data1: pd.Series, capital: pd.Series,
                              n=0) -> pd.Series:
    '''
    data: change dataframe
    data1: cash flow_eod dataframe
    capital: eod capital data
    calculate start cap eod, capital - cash flow for the day when cash flow happened
    '''
    if data1.iloc[0] != 0:
        print('cash flow:', data1.iloc[0])
        data1.iloc[0] = 0
        print('cash flow', data1.iloc[0])
    new_data = data.dropna()
    ind_lst = new_data.index.tolist()
    new_data1 = data1[data1.index.isin(ind_lst)]
    capital = capital[capital.index.isin(ind_lst)]
    if n == 0:
        pass
    else:     
        new_data = new_data.iloc[-n:]
        new_data1 = new_data1.iloc[-n:]
        capital = capital.iloc[-n:]
    print(new_data1)    
    print(new_data)
    print(capital)
    len_data = len(new_data)
    for x in range(len(new_data)):
        new_data.iloc[x] = len_data-1-x
        if new_data1.iloc[x] != 0:
            capital.iloc[x] = capital.iloc[x] - new_data1.iloc[x] 
    print('after for loop new data change', new_data)
    print('capital mwr', capital)
    print('len of wt timeseries', len(new_data))
    new_data = new_data / len(new_data)
    frame = pd.DataFrame(new_data1)
    frame['wt'] = new_data.copy()
    wt_cash = frame.product(axis=1)
    print(wt_cash)
    return wt_cash, capital
    
def cagr(starting_value: float, ending_value: float, duration: int) -> float:
    n = 252/duration
    cagr_ret = ((ending_value/starting_value)**n)-1
    return cagr_ret

def stdev(dataframe: pd.DataFrame, col: str) -> float:
    std = dataframe[col].std()
    return std

def mu(dataframe: pd.DataFrame, col: str) -> float:
    '''
    mean returns
    '''
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
    ind_ret.name = 'S&P'
    stock_ret.name = 'basket'
    data = pd.merge(stock_ret, ind_ret, 
                    left_index=True, right_index=True,
                    how='left')
    print(data)
    matrix = data.cov()
    cov = matrix.loc['basket', 'S&P']
    print(cov)
    #var = np.sqrt(data['S&P'].std())**2
    var = matrix.loc['S&P', 'S&P']
    bet_a = cov/var
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
