import streamlit as st
import yfinance as yf
from typing import *
import time
import functools
from streamlit import *
import sqlite3
from database import create_connection, __str__, read_all

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
    def app_stats(self):
        stats = st.radio("What type of statistics do you want to view",
                    ("MWR", "TWR"), horizontal=True)
        if stats=="MWR":
            st.success("MWR")
        elif stats=="TWR":
            st.success("TWR")
    
    def get_data(self):
        pass
    
    def calculate_returns(self):
        pass
    
    @get_index_info
    def app_interact(self):
        placeholder=st.empty()
        while True:
            print(self.news1)
            news=self.news1[-1]
            ref_news='Latest Headline: \n'+news['title']
            placeholder.info(ref_news, icon='📰')
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