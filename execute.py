from database import database
import streamlit as st

def main() -> object:
    obj = database(database_name=st.secrets["database"]['database_name'], 
                   table_name=st.secrets["database"]["table_name"],
                   ticker='^GSPC')
    conn = obj.create_connection()
    success = obj.__str__()
    print(conn, success)
    date = obj.get_last_working_day()
    data =  obj.fetch_data()
 #   table = obj.create_historical_prices_table()
    rec = obj.insert_records()
    data1 = obj.read_all()
    close = obj.close_connection()
 #   return conn, success, data, table, rec, close
    
    return conn, data, data1
execute = main()
