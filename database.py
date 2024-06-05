import sqlite3
from typing import *
import yfinance as yf
import pandas as pd
import streamlit as st
import datetime
from datetime import timedelta
import os

class database:
    def __init__(self, database_name: str, table_name: str, ticker: str) -> None:
        self.database_name = database_name   
        self.table_name = table_name
        self.ticker = ticker

    def get_last_working_day(self) -> None:
        today = datetime.datetime.today()
        weekday = today.weekday()

        if weekday == 0:  # Monday
            days_to_subtract = 3
        elif weekday == 6:  # Sunday
            days_to_subtract = 2
        else:
            days_to_subtract = 1

        last_working_day = today - datetime.timedelta(days=days_to_subtract)
        self.last_working_day = last_working_day.date()
        self.end_date = today.date()
        
    def fetch_data(self) -> pd.DataFrame:
        nifty = yf.Ticker(self.ticker)
        print(self.last_working_day, self.end_date)
        data = nifty.history(interval='1d', start=str(self.last_working_day), end=str(self.end_date))
        data.to_csv('prices.csv')
        self.data = data
        return data
             
    def create_connection(self) -> Tuple[object, object]:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        self.conn = conn
        self.cursor = cursor
        return conn, cursor
        
    def __str__(self) -> str:
        return "Connection established successfully"
        
    def create_historical_prices_table(self) -> None:
        table=self.table_name
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                date DATE PRIMARY KEY NOT NULL,
                Open FLOAT,
                High FLOAT,
                Low FLOAT,
                Close FLOAT,
                Volume INTEGER
            )
    ''')

    def insert_records(self) -> None:
        for index, row in self.data.iterrows():
            self.cursor.execute('''
                INSERT INTO {} (Date, Open, High, Low, Close, Volume)
                VALUES (?, ?, ?, ?, ?, ?)
            '''.format(self.table_name), (index.date(), row['Open'],
                                          row['High'], row['Low'], row['Close'], 
                                          row['Volume']))
                    
    def read_all(self) -> None:
        self.cursor.execute(f'''SELECT * FROM {self.table_name}''')
        rows = self.cursor.fetchall()
        print(rows[0])
        print(rows[-1])
        return rows

    def close_connection(self) -> None:
        self.conn.commit()
        self.conn.close()
    

# data = nifty.history(interval='1d', start='2019-01-01', end='2024-06-03') [historical fill]
#execute = main()
#import yfinance as yf
#nifty = yf.Ticker('^GSPC')
#data = nifty.history(interval='1d', start='2024-05-31', end='2024-06-03')
#print(data)
