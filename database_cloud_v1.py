from typing import *
import yfinance as yf
import pandas as pd
import datetime
from datetime import timedelta
import os
from streamlit_gsheets import GSheetsConnection
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import ast

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
        data = nifty.history(interval='1d', start=str(datetime.date(2022,12,30)), end=str(datetime.date(2024,7,24)))
        #data = nifty.history(interval='1d', start=str(self.last_working_day), end=str(self.end_date))
        data["Date"] = data.index.date
        data = data.reset_index(drop=True)
        self.data = data
        return data
             
    def create_connection(self) -> Tuple[object, object]:
        cred_dict = json.loads(os.environ["dict1"])
        scope = ['https://spreadsheets.google.com/feeds', 
                 'https://www.googleapis.com/auth/drive'] 
        creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict)
        client = gspread.authorize(creds) 
        print("authorization completed successfully")
        lst_sheets = ast.literal_eval(os.environ["sheetname"])
        print(os.environ["sheetname"], type(os.environ["sheetname"]), type(lst_sheets))
        sh = client.open(os.environ["filename"]).worksheet(lst_sheets[5])        
        self.sh = sh
        
    def __str__(self) -> str:
        return "Connection established successfully"
    

    def write_data(self):
        self.data["Date"] = self.data["Date"].astype(str)
        values = self.data.values.tolist()
        self.sh.append_row(self.data.columns.tolist(), value_input_option="USER_ENTERED")
        self.sh.append_rows(values, value_input_option="USER_ENTERED")  
    
obj = database(ticker='^GSPC')
date = obj.get_last_working_day()
data = obj.fetch_data()
conn = obj.create_connection()
success = obj.__str__()
print(conn, success)
print(obj.write_data())
