import streamlit as st
import yfinance as yf
from typing import *
import time
import functools


class app:
    def __init__(self, ticker='^GSPC'):
        self.ticker = ticker

    def get_index_info(self, func):
        @functools.wrap(func)
        def get_news(self):
            index=yf.Ticker(self.ticker)
            news1=index.news
            self.news1=news1
            if len(news1)!=0:
                return func()
            else:
                pass

    @get_index_info
    def app_interact(self):
        pass

    @classmethod
    def method(clf):
        '''
        creates a new object from existing object
        '''
        pass
    pass

