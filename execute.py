from database import database
import streamlit as st
import toml

def main() -> object:

   # Load data from secrets.toml
    with open(".streamlit\secrets.toml", "r") as f:
      secrets_data = toml.load(f)

    # Access specific secrets (e.g., API keys)
    print(type(secrets_data)), print(secrets_data['database']['database_name'])
    '''
    obj = database(database_name=st.secrets["database"]['database_name'], 
                   table_name=st.secrets["database"]["table_name"],
                   ticker='^GSPC')
   '''
    obj = database(database_name=secrets_data["database"]['database_name'], 
                   table_name=secrets_data["database"]["table_name"],
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
