import streamlit as st
def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.set_page_config(page_title='Dashboard', page_icon='htts_fund_logo.png', layout='wide')
    st.sidebar.success('Select Any Page From Here')
    st.sidebar.page_link("pages/baskets_analysis.py", label="Compare your baskets with s&p")
    st.sidebar.page_link("pages/_index_analysis.py", label="S&P Analysis")

authenticated_menu()

#import yfinance as yf
#news=yf.Ticker('^GSPC')
#print(news.news[-1]['title'])