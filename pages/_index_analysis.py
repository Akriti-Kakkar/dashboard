import streamlit as st
import yfinance as yf
from typing import *
import functools
from streamlit import *
import sqlite3
from database import database
import pandas as pd
import altair as alt
from datetime import timedelta
import numpy as np
import datetime
from stats import *
import plotly.express as px


class app:
    def __init__(self, ticker='^GSPC'):
        self.ticker = ticker
        
    @staticmethod
    def page_config():
        st.set_page_config(page_title='Dashboard', page_icon='🌎', layout='wide')
        st.sidebar.image('htts_fund_logo.png', caption='HTTS Fund')
        st.subheader('📈 S&P Analysis')
        st.markdown('##')
        
    def get_index_info(func):
        @functools.wraps(func)
        def get_news(self):
            while True:
                index=yf.Ticker(self.ticker)
                news1=index.news
                print(news1)
                self.news1=news1
                if len(self.news1)!=0:
                    print('if block')
                    return func(self)
                else:
                    print('else block')
                    pass
        return get_news
    
    def get_data(self):
        obj = database(database_name=st.secrets["database"]['database_name'], 
                   table_name=st.secrets["database"]["table_name"],
                   ticker='^GSPC')
        conn = obj.create_connection()
        success = obj.__str__()
        print(conn, success)
        data1 = obj.read_all()
        data = pd.DataFrame(data1)
        data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        data = data.set_index('Date', drop=True)
        data.index = pd.to_datetime(data.index)
        self.data = data
        
    def calculate_returns(self):
        self.data['returns'] = self.data['Close'].pct_change()
        self.data['pnl'] = self.data['Close'] - self.data['Close'].shift(1)
        self.data['mwr'] = self.data['pnl'] / self.data['Close'].shift(1)
        self.data = self.data.fillna(0)
    
    def duration_widgets(self):
        col3, col4, col5, col6, col30 = st.columns(5)
        with col3:
            placeholder = st.empty()
        with col4:
            placeholder1 = st.empty()
        with col5:
            placeholder2 = st.empty()
        with col6:
            placeholder3 = st.empty()
        with col30:
            placeholder30 = st.empty()
        self.placeholder = placeholder
        self.placeholder1 = placeholder1
        self.placeholder2 = placeholder2
        self.placeholder3 = placeholder3
        self.placeholder30 = placeholder30
    
    def placeholders(self):
        placeholder4 = st.empty()
        placeholder31 = st.empty()
        self.placeholder4 = placeholder4
        self.placeholder31 = placeholder31
    
    def app_stats(self, analysis_data, allocation):
        col7, col8, col9, col10 = st.columns(4)
        with col7:
            st.info('Open', icon='📌')
            try:
                st.metric('Open', value=f"${analysis_data['Open'].iloc[0]:,.0f}")
            except IndexError:
                st.metric('Open', value=f'{np.nan}')
            finally:
                st.info('1D Return', icon='📌')
                try:
                    st.metric('1D Return', value=f"{analysis_data['mwr'].iloc[-1]*100:,.2f}%")
                except IndexError:
                    st.metric('1D Return', value=f'{np.nan}')
            allocation = allocation
            st.info('Positive Days', icon='📌')
            try:
                pos_days = win_days(analysis_data, 'mwr')
                st.metric('Positive Days', f"{pos_days} Days")
            except:
                st.metric('Positive Days', np.nan)
            st.info('Negative Days', icon='📌')
            try:
                neg_days = loss_days(analysis_data, 'mwr')
                st.metric('Negative Days', f"{neg_days} Days")
            except:
                st.metric('Negative Days', np.nan)    
            st.info('Duration', icon='📌')
            days = duration(analysis_data.index.min().date(), analysis_data.index.max().date())
            st.metric('Duration', f"{days} Days")          

        with col8:
            st.info('High', icon='📌')
            st.metric('High', value=f"${analysis_data['High'].max():,.0f}") 
            try:
                ret_ = analysis_data.iloc[-21:]
                pft = ret_['Close'].iloc[len(ret_)-1]-ret_['Close'].iloc[0] 
                ret_met = pft/ret_['Close'].iloc[0]
                st.info('21D Return', icon='📌')
                st.metric('21D Return', value=f"{ret_met*100:,.2f}%") 
            except IndexError:
                st.info('21D Return', icon='📌')
                st.metric('21D Return', value=f'{np.nan}') 
            st.info('Positive PnL (%)', icon='📌')
            positive_pnl = analysis_data.copy()
            positive_pnl.query('pnl>0', inplace=True)
            negative_pnl = analysis_data.copy()
            negative_pnl.query('pnl<0', inplace=True)
            pos_pnl = sum(positive_pnl['pnl'])/analysis_data.loc[analysis_data.index.min(), 'Close']
            pos_pnl1 = allocation * pos_pnl             
            st.metric('Positive PnL (%)', value=f"{pos_pnl*100:,.2f}%")
            st.info('Positive PnL', icon='📌')
            st.metric('Positive PnL', value=f"${pos_pnl1:,.0f}")      
            st.info('Win-Loss Ratio', icon='📌')
            wl_ratio = win_loss(pos_days, neg_days)
            st.metric('Win-Loss Ratio', value=f"{wl_ratio:,.2f}")  
  
        with col9:
            st.info('Low', icon='📌')
            st.metric('Low', value=f"${analysis_data['Low'].min():,.0f}")  
            try:
                ret_1 = analysis_data.iloc[-60:]
                pft1 = ret_1['Close'].iloc[len(ret_1)-1]-ret_1['Close'].iloc[0] 
                ret_met1 = pft1/ret_1['Close'].iloc[0]
                st.info('60D Return', icon='📌')
                st.metric('60D Return', value=f"{ret_met1*100:,.2f}%")    
            except IndexError:
                st.info('60D Return', icon='📌')
                st.metric('60D Return', value=f'{np.nan}') 
            neg_pnl = sum(negative_pnl['pnl'])/analysis_data.loc[analysis_data.index.min(), 'Close'] 
            neg_pnl1 = allocation * neg_pnl
            st.info('Negative PnL (%)', icon='📌')
            st.metric('Negative PnL (%)', value=f"{neg_pnl*100:,.2f}%")
            st.info('Negative PnL', icon='📌')
            st.metric('Negative PnL', value=f"${neg_pnl1:,.0f}")
            win_pctt = win_pct(pos_days, days)
            st.info('Winning Pct', icon='📌')
            st.metric('Winning Pct', value=f"{(win_pctt * 100):,.2f}%")            

                                             
        with col10:
            st.info('Close', icon='📌')
            try:
                st.metric('Close', value=f"${analysis_data['Close'].iloc[-1]:,.0f}")   
            except IndexError:
                st.metric('Close', value=f'{np.nan}')   
            finally:                    
                st.info('Period Return', icon='📌')  
                try:
                    pft2 = analysis_data['Close'].iloc[len(analysis_data)-1]-analysis_data['Close'].iloc[0]
                    ret_met2 = pft2/analysis_data['Close'].iloc[0]
                    st.metric('Period Return', value=f"{ret_met2*100:,.2f}%")  
                except IndexError:
                    st.metric('Period Return', value=f'{np.nan}')   
            pnl_dynamic =  allocation*ret_met2      
            end_value = allocation + pnl_dynamic   
            st.info('PnL', icon='📌')  
            st.metric('PnL', value=f"${pnl_dynamic:,.0f}")     
            st.info('Ending Value', icon='📌')   
            st.metric('Ending Value', value=f"${end_value:,.0f}")    
            ann_ret = cagr(allocation, end_value, days)
            st.info('CAGR', icon='📌')   
            st.metric('CAGR', value=f"{ann_ret * 100:,.2f}%")  
            
    def app_stats_mwr(self, analysis_data, allocation):
        analysis_data['ec'] = (1 + analysis_data['returns']).cumprod() * allocation
        start = analysis_data.index.min().date()
        end = analysis_data.index.max().date()
        st.table(pd.DataFrame({'Starting Date': [start], 'Latest Ending Date': [end]},
                                  index=['TimeStamps']))
        mwr_col1, mwr_col2 = st.columns(2)
        st.subheader('Detailed Risk Analysis')
        st.write('downside deviation', 'avg drawdown', 'max drawdown', 'graph drawdown')
        st.subheader('Detailed Risk Return Analysis')
        st.write('sharpe ratio', 'sortino ratio', 'graph returns and std')
        with mwr_col1:
            fig = px.line(analysis_data, y = 'ec', x = analysis_data.index,
                            template='plotly_white')
            fig.update_layout(plot_bgcolor="#FFFFFF", 
                                yaxis_title="Equity Curve ($)",
                                xaxis_title="Date")                  
            st.plotly_chart(fig)  
        with mwr_col2:
            active = duration(start, end)
            end_all = analysis_data.loc[analysis_data.index[-1], 'ec']
            ret = cagr(allocation, end_all, active)
            mn_ret = mu(analysis_data, 'returns')
            stde = stdev(analysis_data, 'returns')
            ann_vol = annualized_vol(stde)
            shp = sharpe_ratio(ret, ann_vol)
            dd = drawdown(analysis_data, 'ec')
            mdd = max_drawdown(dd)
            ad = avg_drawdown(dd) 
            wn_d = win_days(analysis_data, 'returns')
            ln_d = loss_days(analysis_data, 'returns')
            wn = win_pct(wn_d, active)
            wl = win_loss(wn_d, ln_d)
            dow = downside_deviation(analysis_data, 'returns')
            sort1 = sortino_ratio(ret, dow)
            max_cons_pos = getMaxLength(analysis_data['returns'], 1)
            max_cons_neg = getMaxLength(analysis_data['returns'], 0)
            m_ret = avg_monthly_return(analysis_data, 'returns')
            print(m_ret)
            
            stats_data = pd.DataFrame({
                'Stats' : ['Duration',
                           'Starting Value', 'Deposits/Withdrawals',
                           'Ending Value', 'Mean Return', 
                           'Average Monthly Return', 'Stdev',
                           'CAGR', 'Annualized Volatility',
                           'Sharpe Ratio', 'Sortino Ratio', 
                           'Average Drawworn', 'Maximum Drawdown',
                           'Winning Pct', 'Win-Loss Ratio',
                           'Max Consecutive Positive Days',
                           'Max Consecutive Negative Days'],
                
                'Values' : [f'{active} Days', f'${allocation:,.2f}', f'${0:,.2f}', 
                            f'${end_all:,.2f}', f'{mn_ret*100:,.2f}%',
                            f'{m_ret*100:,.2f}%', f'{stde*100:,.2f}%',
                            f'{ret*100:,.2f}%', f'{ann_vol*100:,.2f}%', f'{shp:,.2f}',
                            f'{sort1:,.2f}', f'{ad*100:,.2f}%', f'{mdd*100:,.2f}%', f'{wn*100:,.2f}%',
                            f'{wl:,.2f}', max_cons_pos, max_cons_neg]
            })
            stats_data.index = stats_data.index + 1
            st.table(stats_data)
    
    def switch_stats(self):
        stats = st.radio("Choose Type Of Stats",
                    ("MWR", "TWR"), horizontal=True,
                    help='''
                    Money Weighted Returns (Modified Dietz Method): 
                    Ending Value - Initial - Cash Flow/Initial Value + Weighted Cash Flow
                    
                    Time Weighted Returns (Compounded Returns):
                    [(1 + RN) * (1 + RN) * ... -1] * 100
                    
                    where,
                    RN = Ending Value/(Initial Value + Cash Flow)-1 
                    ''')
        
        stats1 = st.radio('Choose PnL Basis', ("Change", "MTM", "MTM (Exc. Forex)"), 
                        horizontal=True,
                        help='''
                        
                        Change = mark-to-market valuations of assets including forex - 
                        cost (commision, interest, taxes, etc) +
                        dividend - accruals charges + accrual income - basket-level charges +
                        basket-level income
                        
                        MTM = mark-to-market valuations of assets including forex - 
                        cost (commision, interest, taxes, etc) +
                        dividend
                        
                        MTM (Exc. Forex) = mark-to-market valuations of assets excluding forex - 
                        cost (commision, interest, taxes, etc) +
                        dividend''')
        

        if stats=="MWR":
            st.success("MWR")
            placeholder = st.empty()
            self.duration_widgets()  
            def default():
                start_date = self.placeholder.date_input('Start Date', self.data.index[0].date(), 
                                    min_value=self.data.index[0],
                                    max_value=self.data.index[len(self.data)-1])
                end_date = self.placeholder1.date_input('End Date', self.data.index[len(self.data)-1],
                                    min_value=self.data.index[0],
                                    max_value=self.data.index[len(self.data)-1])   
                try:
                    analysis_data1 = self.data.loc[start_date:end_date]
                    analysis_data = date_range(start_date, end_date, analysis_data1)
                    analysis_data[['Open', 'High', 'Low', 'Close']] = analysis_data[['Open',
                                                                                     'High', 'Low',
                                                                                     'Close']].fillna(
                    method=('ffill'))
                    analysis_data[['pnl', 'returns', 'mwr', 'Volume']] = analysis_data[['pnl', 
                                                                                       'returns', 
                                                                                       'mwr',
                                                                                       'Volume']].fillna(0)
                except IndexError:
                    st.write('start date should be less than or equal to end date') 
                self.placeholders()   
                allocation = self.placeholder4.number_input('Initial Allocation', 
                                                min_value=float(analysis_data['Close'].iloc[0]),
                                                value=float(analysis_data['Close'].iloc[0]), 
                                                step=100000.00, max_value=100000000000000000.00,
                                                help='''
                                                Assumes that index share was bought in the end
                                                of day1. Hence, Initial Allocation is close 
                                                price at day 1. You can modify it to any value
                                                you want to view''')                                                
                self.app_stats(analysis_data, allocation) 
                analysis_data['Daily Money-Weighted Returns'] = analysis_data['mwr'] * 100
                fig = px.line(analysis_data, y = 'Daily Money-Weighted Returns', x = analysis_data.index,
                             template='plotly_white')
                fig.update_layout(plot_bgcolor="#FFFFFF", 
                                  yaxis_title="Daily Money-Weighted Returns (%)",
                                  xaxis_title="Date")                  
                st.plotly_chart(fig)                   
                
            def view_21():
                if st.session_state['button'] == True:
                    st.session_state['button'] = False
                analysis_data1 = self.data
                start_date = analysis_data1.index.min()
                end_date = analysis_data1.index.max()
                analysis_data11 = date_range(start_date, end_date, analysis_data1)
                analysis_data = analysis_data11.iloc[-21:]
                analysis_data[['Open', 'High', 'Low', 'Close']] = analysis_data[['Open',
                                                                                    'High', 'Low',
                                                                                    'Close']].fillna(
                method=('ffill'))
                analysis_data[['pnl', 'returns', 'mwr', 'Volume']] = analysis_data[['pnl', 
                                                                                    'returns', 
                                                                                    'mwr',
                                                                                    'Volume']].fillna(0)                
                self.placeholders()
                allocation = self.placeholder4.number_input('Initial Allocation', 
                                                min_value=analysis_data['Close'].iloc[0],
                                                value=analysis_data['Close'].iloc[0],
                                                step=100000.00)                 
                self.app_stats(analysis_data, allocation) 
                analysis_data['Daily Money-Weighted Returns'] = analysis_data['mwr'] * 100
                fig = px.bar(analysis_data, x = 'Daily Money-Weighted Returns', y = analysis_data.index,
                             template='plotly_white')
                fig.update_layout(plot_bgcolor="#FFFFFF", 
                                  xaxis_title="Daily Money-Weighted Returns (%)",
                                  yaxis_title="Date")                  
                st.plotly_chart(fig)                      
                
            def view_60():
                analysis_data1 = self.data
                start_date = analysis_data1.index.min()
                end_date = analysis_data1.index.max()
                analysis_data11 = date_range(start_date, end_date, analysis_data1)
                analysis_data = analysis_data11.iloc[-60:]
                analysis_data[['Open', 'High', 'Low', 'Close']] = analysis_data[['Open',
                                                                                    'High', 'Low',
                                                                                    'Close']].fillna(
                method=('ffill'))
                analysis_data[['pnl', 'returns', 'mwr', 'Volume']] = analysis_data[['pnl', 
                                                                                    'returns', 
                                                                                    'mwr',
                                                                                    'Volume']].fillna(0)                
                self.placeholders() 
                allocation = self.placeholder4.number_input('Initial Allocation', 
                                        min_value=float(analysis_data['Close'].iloc[0]),
                                        value= float(analysis_data['Close'].iloc[0]),
                                        max_value=100000000.0000, step=100000.00)
                self.app_stats(analysis_data, allocation)  
                analysis_data['Daily Money-Weighted Returns'] = analysis_data['mwr'] * 100
                fig = px.bar(analysis_data, x = 'Daily Money-Weighted Returns', y = analysis_data.index,
                             template='plotly_white')
                fig.update_layout(plot_bgcolor="#FFFFFF", 
                                  xaxis_title="Daily Money-Weighted Returns (%)",
                                  yaxis_title="Date")                  
                st.plotly_chart(fig)                      
                           
            button1 = self.placeholder3.button('Last 60 Days')
            button2 = self.placeholder2.button('Last 21 Days')
            button3 = self.placeholder30.button('Exit View')

            if st.session_state.get('button')!=True:
                st.session_state['button'] = button1 # Saved the state
            if st.session_state.get('new_button')!=True:
                st.session_state['new_button'] = button2 # Saved the state   
            if st.session_state.get('new_button1')!=True:
                st.session_state['new_button1'] = button3  
            
         #   if ((st.session_state['button'] == True) and (st.session_state['new_button'] ==  True)):
         #       st.rerun()              
                           
            if st.session_state['new_button1'] == True:
                st.session_state['button'] = False
                st.session_state['new_button'] = False
                st.session_state['new_button1'] = False

            if (st.session_state['button'] == True) and (st.session_state['new_button'] == True):
                st.warning('''Click On 'Exit View' before switching between views''')
            
            elif st.session_state['button'] == True:
                st.session_state['new_button'] = False
                view_60()
                        
            elif st.session_state['new_button'] == True:
                st.session_state['button'] = False
                view_21()
                
                
            elif (st.session_state['button']!=True) and (st.session_state['new_button']!=True):
                default()
            
                

        elif stats=="TWR":
            st.success("TWR")
            self.duration_widgets()  
            def default():
                start_date = self.placeholder.date_input('Start Date', self.data.index[0].date(), 
                                    min_value=self.data.index[0],
                                    max_value=self.data.index[len(self.data)-1])
                end_date = self.placeholder1.date_input('End Date', self.data.index[len(self.data)-1],
                                    min_value=self.data.index[0],
                                    max_value=self.data.index[len(self.data)-1])   
                try:
                    analysis_data1 = self.data.loc[start_date:end_date]
                    analysis_data = date_range(start_date, end_date, analysis_data1)
                    analysis_data[['Open', 'High', 'Low', 'Close']] = analysis_data[['Open',
                                                                                     'High', 'Low',
                                                                                     'Close']].fillna(
                    method=('ffill'))
                    analysis_data[['pnl', 'returns', 'mwr', 'Volume']] = analysis_data[['pnl', 
                                                                                       'returns', 
                                                                                       'mwr',
                                                                                       'Volume']].fillna(0)
                except IndexError:
                    st.write('start date should be less than or equal to end date') 
                self.placeholders()   
                allocation = self.placeholder4.number_input('Initial Allocation', 
                                                min_value=float(1.00),
                                                value=float(100000.00), 
                                                step=100000.00, max_value=100000000000000000.00,
                                                help='''
                                                Assumes that index share was bought in the end
                                                of day1. Hence, Initial Allocation is close 
                                                price at day 1. You can modify it to any value
                                                you want to view''')                                                
                self.app_stats_mwr(analysis_data, allocation) 
            default()   
            
    def app_interact(self):                 
        self.get_data()
        self.calculate_returns()
        self.switch_stats()

    @classmethod
    def method(clf):
        '''
        creates a new object from existing object
        '''
        pass
    
    def main(self):
        return self.page_config(),  self.app_interact()
    

def run():
    initial=app(ticker='^GSPC')
    return initial.main()
run()
