import sqlite3
from typing import *
import yfinance as yf
import pandas as pd
import streamlit as st
import datetime
from datetime import timedelta
import os
from streamlit_gsheets import GSheetsConnection
from oauth2client.service_account import ServiceAccountCredentials
#import auth
#from auth import spreadsheet_service
#from auth import drive_service
# Authentication and access modules
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
        conn = st.connection("gsheets", type=GSheetsConnection)
       # scope = ['https://spreadsheets.google.com/feeds', 
       #          'https://www.googleapis.com/auth/drive'] 
       # creds = ServiceAccountCredentials.from_json_keyfile_name('dashbaord-428313-6b44afcabf16.json', scope) 
       # client = gspread.authorize(creds) 
       # sh = client.open("dashboard_2024").worksheet("s&p")
       
       
       # creds = ServiceAccountCredentials.from_json_keyfile_name(filename="dashbaord-428313-6b44afcabf16.json")
      #                                                           scopes=["https://accounts.google.com/o/oauth2/auth",
      #                                                                   "https://oauth2.googleapis.com/token",
      #                                                                   "https://www.googleapis.com/oauth2/v1/certs",
      #                                                                   "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-app%40dashbaord-428313.iam.gserviceaccount.com"])
        #                                                         scopes="https://docs.google.com/spreadsheets/d/1QW5VRSxyhvHdq9L5YJA_49Uaim5b9A8hCClVNKF2hec/edit?usp=sharing")
        #cred = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        #client = gspread.authorize(creds)
        self.conn = conn
        #self.creds = creds
        #self.client = client
        #self.sh = sh
        
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
        frame = self.conn.read(worksheet="s&p")
        last_row = len(frame)
        fst_use = last_row+1
        len_app = len(self.data)
        lst_use = last_row + len_app
        num = len(self.data.columns)
        print("num", num)
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
        cell = search_num(num) 
        print("cell", cell)   
        range_name = "Sheet1!A{0}:{1}{2}".format(fst_use, cell, lst_use) 

        self.data.to_json("data.json")
        self.data = self.data.drop("Date", axis=1)
        values = self.data.values.tolist()
        #self.sh.append_rows(values)
        
        #self.conn.update(worksheet="s&p", data=self.data, cell_range = range_name) 
        #self.conn.append(worksheet="s&p", range_to_append=range_name, data_to_append=self.data)
        #sh = self.conn.update()
        self.conn.values().update(range, valueInputOption="USER_ENTERED", body={"values":values}).execute()  # try this as well
        
        '''
        sh = self.client.open("https://docs.google.com/spreadsheets/d/1QW5VRSxyhvHdq9L5YJA_49Uaim5b9A8hCClVNKF2hec/edit?usp=sharing")
        worksheet = sh.get_worksheet("s&p")
        worksheet.append_rows(self.data)
        
    #    range_name = "Sheet1!A{0}:{1}{2}".format(fst_use, cell, lst_use)
    #    values = self.data
    #    value_input_option = 'USER_ENTERED'
    #    body = {
    #        'values': values
    #    }
    #    result = spreadsheet_service.spreadsheets().values().update(
    #        spreadsheetId=spreadsheet_id, range=range_name,
    #        valueInputOption=value_input_option, body=body).execute()
     '''   
        
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
obj = database(ticker='^GSPC')
date = obj.get_last_working_day()
data = obj.fetch_data()
conn = obj.create_connection()
success = obj.__str__()
print(conn, success)
print(obj.write_data())
