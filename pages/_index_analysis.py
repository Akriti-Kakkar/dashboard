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
    
    def app_stats(self):
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            start_date = st.date_input('Start Date', self.data.index[0].date())
        with col4:
            end_date = st.date_input('End Date', self.data.index[-1])
        with col5:
            if st.button('Last 21 Days'):
                analysis_data = self.data.iloc[-21:]
        with col6:
            if st.button('Last 60 Day'):
                analysis_data = self.data.iloc[-60:]
        try:
            analysis_data = analysis_data.copy()
        except NameError:
            try:
                analysis_data = self.data.loc[start_date:end_date]
            except IndexError:
                st.write('start date should be less than or equal to end date')
        stats = st.radio("What type of statistics do you want to view",
                    ("MWR", "TWR"), horizontal=True)
        col7, col8, col9, col10 = st.columns(4)
        with col7:
            st.info('Open', icon='📌')
            try:
                st.metric('Open', value=f'{analysis_data['Open'].iloc[0]:,.0f}')
            except IndexError:
                st.metric('Open', value=f'{np.nan}')
        with col8:
            st.info('High', icon='📌')
            st.metric('High', value=f'{analysis_data['High'].max():,.0f}')  
        with col9:
            st.info('Low', icon='📌')
            st.metric('Low', value=f'{analysis_data['Low'].min():,.0f}')          
        with col10:
            st.info('Close', icon='📌')
            try:
                st.metric('Close', value=f'{analysis_data['Close'].iloc[-1]:,.0f}')       
            except IndexError:
                st.metric('Open', value=f'{np.nan}')                      
        if stats=="MWR":
            st.success("MWR")
            col1, col2 = st.columns(2)
            with col1:
                st.line_chart(analysis_data, y=['Close'],
                            use_container_width=True)
                st.write(analysis_data)
        elif stats=="TWR":
            st.success("TWR")
            try:
                st.plotly_chart(self.data['Close'], use_container_width=False)
            except IndexError:
                st.info('''End date should be greater than or equal to start date. 
                            Only select historical dates''')
            
    @get_index_info
    def app_interact(self):
        placeholder=st.empty()
        while True:
            print(self.news1)
            news=self.news1[-1]
            ref_news='Latest Headline: \n'+news['title']
            placeholder.info(ref_news, icon='📰')
            self.get_data()
            self.app_stats()
            time.sleep(360)

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