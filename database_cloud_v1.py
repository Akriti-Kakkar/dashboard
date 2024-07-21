import sqlite3
from typing import *
import yfinance as yf
import pandas as pd
import streamlit as st
import datetime
from datetime import timedelta
import os
from streamlit_gsheets import GSheetsConnection
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

class database:
    def __init__(self, ticker: str) -> None:
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
        data["Date"] = data.index
        data = data.reset_index(drop=True)
        data.to_csv('prices.csv')
        self.data = data
        return data
             
    def create_connection(self) -> Tuple[object, object]:
       # conn = st.connection("gsheets", type=GSheetsConnection)
        cred_dict = json.loads(os.environ["dict1"])
        scope = ['https://spreadsheets.google.com/feeds', 
                 'https://www.googleapis.com/auth/drive'] 
        creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict)
        client = gspread.authorize(creds) 
        print("authorization completed successfully")
        sh = client.open(os.environ["filename"]).worksheet(os.environ["sheetname"])
        print("client read the file and the sheet")
        self.sh = sh
        
    def __str__(self) -> str:
        return "Connection established successfully"
    
    def get_alpha(self):
        
        alpha='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        def search_num(num):
            if num < 26:
                return alpha[num-1]
            else:
                q, r = num//26, num%26
                if r == 0:
                    if q == 1:
                        return alpha[r-1]
                    else:
                        return search_num(q-1)+alpha[r-1]
                else:
                    return search_num(q)+alpha[r-1]
        lst = []
        for num in [26, 51, 52, 80, 676, 702, 705]:
            lst.append(search_num(num))
        return lst
                
        
    def write_data(self):
        self.data = self.data.drop("Date", axis=1)
        values = self.data.values.tolist()
        self.sh.append_rows(values)  
        
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
    
obj = database(ticker='^GSPC')
date = obj.get_last_working_day()
data = obj.fetch_data()
conn = obj.create_connection()
success = obj.__str__()
print(conn, success)
print(obj.write_data())
