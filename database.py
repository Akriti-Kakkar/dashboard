import sqlite3
from typing import *
import yfinance as yf
import pandas as pd
import streamlit as st

class database:
    def __init__(self, database_name: str, table_name: str, ticker: str) -> None:
        self.database_name = database_name   
        self.table_name = table_name
        self.ticker = ticker
        
    def fetch_data(self) -> pd.DataFrame:
        nifty = yf.Ticker(self.ticker)
        data = nifty.history(interval='1d', start='2019-01-01', end='2024-06-03')
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
            CREATE TABLE IF NOT EXISTS index_prices (
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
    
def main() -> object:
    obj = database(database_name=st.secrets['database_name'], table_name=st.secrets["table_name"],
                   ticker='^GSPC')
    conn = obj.create_connection()
    success = obj.__str__()
    print(conn, success)
    data = obj.read_all()
 #   data =  obj.fetch_data()
 #   table = obj.create_historical_prices_table()
 #   rec = obj.insert_records()
    close = obj.close_connection()
 #   return conn, success, data, table, rec, close
    
    return conn, data
execute = main()