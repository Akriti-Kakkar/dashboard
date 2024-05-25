import streamlit as st
import yfinance as yf
from typing import *
import time
import functools


class app:
    def __init__(self, ticker='^GSPC'):
        self.ticker = ticker

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
                time.sleep(10)
        return get_news

    @get_index_info
    def app_interact(self):
        placeholder=st.empty()
        while True:
            print(self.news1)
            news=self.news1[-1]
            ref_news='Latest Headline: \n'+news['title']
            placeholder.info(ref_news, icon='📰')
            time.sleep(20)

    @classmethod
    def method(clf):
        '''
        creates a new object from existing object
        '''
        pass
    
    def main(self):
        return self.app_interact()
    
