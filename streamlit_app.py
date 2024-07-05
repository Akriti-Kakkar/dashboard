import streamlit as st
from PIL import Image
import sqlite3
def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.set_page_config(page_title='Dashboard', page_icon='htts_fund_logo.jpg', layout='wide')
    # Load your image
    image = Image.open("htts_fund_logo.png")
    st.sidebar.image(image, caption="HTTS Fund", output_format="PNG")
    st.header('Performance Analysis Dashboard')
    st.sidebar.markdown('''
                        <span style="color:white;font-weight:700;font-size:25px;background-color:black">
                            Select Any Page From Here:
                        </span>
                        ''', 
                        unsafe_allow_html=True)
    st.sidebar.page_link("pages/baskets_analysis.py", label="Compare your baskets with s&p")
    st.sidebar.page_link("pages/_index_analysis.py", label="S&P Analysis")
    conn = sqlite3.connect(st.secrets["database"]["database_name"])
    cursor = conn.cursor()
    st.write(cursor.execute(f'''SELECT * FROM {st.secrets["database"]["table_name"]}'''))

authenticated_menu()

#import yfinance as yf
#news=yf.Ticker('^GSPC')
#print(news.news[-1]['title'])