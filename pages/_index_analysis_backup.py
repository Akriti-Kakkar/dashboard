import streamlit as st
import yfinance as yf
from typing import *
import time
import functools
from streamlit import *
import sqlite3
from database import database
import pandas as pd
import altair as alt
from datetime import timedelta
import numpy as np
import datetime

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
                time.sleep(300)
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
    
    
    def app_stats(self):
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            start_date = st.date_input('Start Date', self.data.index[0].date(), 
                                       min_value=self.data.index[0],
                                       max_value=self.data.index[len(self.data)-1])
        with col4:
            end_date = st.date_input('End Date', self.data.index[len(self.data)-1],
                                       min_value=self.data.index[0],
                                       max_value=self.data.index[len(self.data)-1])                                  
        with col5:
            if st.button('Last 21 Days'):
                analysis_data = self.data.iloc[-21:]
        with col6:
            button1 = st.button('Last 60 Days')
            if button1:
                analysis_data = self.data.iloc[-60:]
        try:
            analysis_data = analysis_data.copy()
        except NameError:
            try:
                analysis_data = self.data.loc[start_date:end_date]
            except IndexError:
                st.write('start date should be less than or equal to end date')
        col7, col8, col9, col10 = st.columns(4)
        with col7:
            st.info('Open', icon='📌')
            try:
                st.metric('Open', value=f'${analysis_data['Open'].iloc[0]:,.0f}')
            except IndexError:
                st.metric('Open', value=f'{np.nan}')
            finally:
                st.info('1D Return', icon='📌')
                try:
                    st.metric('1D Return', value=f'{analysis_data['mwr'].iloc[-1]*100:,.2f}%')
                except IndexError:
                    st.metric('1D Return', value=f'{np.nan}')
            st.info('Initial Allocation', icon='📌')
            if 'allocation' not in st.session_state:
                allocation = analysis_data['Close'].iloc[0]
            allocation = st.number_input('Initial Allocation', min_value=analysis_data['Close'].iloc[0],
                                         value=analysis_data['Close'].iloc[0])

        with col8:
            st.info('High', icon='📌')
            st.metric('High', value=f'${analysis_data['High'].max():,.0f}') 
            try:
                ret_ = analysis_data.iloc[-21:]
                pft = ret_['Close'].iloc[len(ret_)-1]-ret_['Close'].iloc[0] 
                ret_met = pft/ret_['Close'].iloc[0]
                st.info('21D Return', icon='📌')
                st.metric('21D Return', value=f'{ret_met*100:,.2f}%') 
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
            st.metric('Positive PnL (%)', value=f'{pos_pnl*100:,.2f}%')
            st.info('Positive PnL', icon='📌')
            placeholder = st.empty()  
            placeholder.metric('Positive PnL', value=f'${pos_pnl1:,.0f}')
        
  
        with col9:
            st.info('Low', icon='📌')
            st.metric('Low', value=f'${analysis_data['Low'].min():,.0f}')  
            try:
                ret_1 = analysis_data.iloc[-60:]
                pft1 = ret_1['Close'].iloc[len(ret_1)-1]-ret_1['Close'].iloc[0] 
                ret_met1 = pft1/ret_1['Close'].iloc[0]
                st.info('60D Return', icon='📌')
                st.metric('60D Return', value=f'{ret_met1*100:,.2f}%')    
            except IndexError:
                st.info('60D Return', icon='📌')
                st.metric('60D Return', value=f'{np.nan}') 
            neg_pnl = sum(negative_pnl['pnl'])/analysis_data.loc[analysis_data.index.min(), 'Close'] 
            neg_pnl1 = allocation * neg_pnl
            st.info('Negative PnL (%)', icon='📌')
            st.metric('Negative PnL (%)', value=f'{neg_pnl*100:,.2f}%')
            st.info('Negative PnL', icon='📌')
            st.metric('Negative PnL', value=f'${neg_pnl1:,.0f}')

                                             
        with col10:
            st.info('Close', icon='📌')
            try:
                st.metric('Close', value=f'${analysis_data['Close'].iloc[-1]:,.0f}')   
            except IndexError:
                st.metric('Close', value=f'{np.nan}')   
            finally:                    
                st.info('Period Return', icon='📌')  
                try:
                    pft2 = analysis_data['Close'].iloc[len(analysis_data)-1]-analysis_data['Close'].iloc[0]
                    ret_met2 = pft2/analysis_data['Close'].iloc[0]
                    st.metric('Period Return', value=f'{ret_met2*100:,.2f}%')  
                except IndexError:
                    st.metric('Period Return', value=f'{np.nan}')   
            pnl_dynamic =  allocation*ret_met2      
            end_value = allocation + pnl_dynamic   
            st.info('PnL', icon='📌')  
            st.metric('PnL', value=f'${pnl_dynamic:,.0f}')     
            st.info('Ending Value', icon='📌')   
            st.metric('Ending Value', value=f'${end_value:,.0f}')
        self.analysis_data = analysis_data     
        self.pos_pnl = pos_pnl
        self.pos_pnl1 = pos_pnl1
        self.placeholder = placeholder     
        self.button1 = button1       
        self.allocation = allocation                    
    
    def switch_stats(self):
        stats = st.radio("What type of statistics do you want to view",
                    ("MWR", "TWR"), horizontal=True,
                    help='''
                    Money Weighted Returns (Simple Returns): 
                    Ending Value - Initial - Cash Flow/Initial Value + Weighted Cash Flow
                    ''')
        
        stats1 = st.radio('', ("Change", "MTM", "MTM (Exc. Forex)"), 
                        horizontal=True)
        if stats=="MWR":
            st.success("MWR")
            self.app_stats()
            if self.button1:
                self.app_stats()
                
            col1, col2 = st.columns(2)
            with col1:
                self.analysis_data = self.analysis_data.rename(
                    columns = {'mwr': 'Money-Weighted Return'})
                st.line_chart(self.analysis_data, y=['Money-Weighted Return'],
                            use_container_width=True)
                st.write(self.analysis_data)
        elif stats=="TWR":
            st.success("TWR")
            try:
                st.write('Coming soon')
            except IndexError:
                st.info('''End date should be greater than or equal to start date. 
                            Only select historical dates''')
            
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