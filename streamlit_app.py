import streamlit as st
from PIL import Image
from streamlit_gsheets import GSheetsConnection
import schedule
from datetime import datetime
import pytz
import time
import pandas as pd
from stats import date_range, win_days, loss_days, duration
import locale
from streamlit_option_menu import option_menu
import streamlit_theme
import streamlit_extras
import streamlit_toggle
import streamlit_vertical_slider
import streamlit.components
import streamlit.commands

class homepage:
    def __init__(self):
        pass

    def page_config(self):
        # Show a navigation menu for authenticated users
        st.set_page_config(page_title='Dashboard', page_icon='🌎', layout="wide",
                           initial_sidebar_state="expanded")
        # Load your image
        image = Image.open("htts_fund_logo.png")
        st.sidebar.image(image, caption="HTTS Fund", output_format="PNG")
        st.header(r":blue-background[:blue[$$Performance$$ $\>$ $$Analysis$$ $\>$ $$Dashboard$$]]")
        st.sidebar.write(r"🔗:blue-background[:blue[$$Navigation$$ $\>$ $$Pane$$]]")
        st.sidebar.page_link("pages/baskets_analysis.py", label=r":blue-background[:blue[$$Compare$$ $\>$ $$your$$ $\>$ $$baskets$$ $\>$ $$with$$ $\>$ $$SnP$$]]",icon="🔗")
        st.sidebar.page_link("pages/_index_analysis.py", label=r":blue-background[:blue[$$SnP$$ $\>$ $$Analysis$$]]",icon="🔗")
        st.sidebar.markdown('<a href="Akriti.Kakkar@httsfund.com">Email: Akriti.Kakkar@httsfund.com</a>', unsafe_allow_html=True)
        st.markdown("""
        <style> section[data-testid="stSidebar"] { width: 400px !important; }
        </style>
        """, unsafe_allow_html=True)
        st.divider()
        st.subheader(r":blue-background[:blue[$$Year$$ $\>$ $$In$$ $\>$ $$Review$$]]")
    
    
    def connections(self):
        conn = st.connection("gsheets", type=GSheetsConnection)
        self.conn = conn
     
    def read_data(self):
        read_obj1 = self.conn.read(worksheet="change", ttl="300m")
        read_obj1 = read_obj1.set_index("Date")
        read_obj1.index = pd.to_datetime(read_obj1.index)
        start = read_obj1.index.min()
        end = read_obj1.index.max()
        change_frame = date_range(start, end, read_obj1)
        change_frame["Year"] = change_frame.index.year
        lst_yr = read_obj1["Year"].max()
        self.change_frame = change_frame
        self.read_obj1 = read_obj1
        self.lst_year = lst_yr
        
    def create_stats(self):
        frame = self.change_frame[self.change_frame["Year"]==self.lst_year]
        frame = frame.fillna(0)
        baskets_lst = frame.columns.tolist()[2:]
        drop_baskets = [x for x in baskets_lst if (x.endswith("_unmerged"))|(x.endswith("_removed"))|(x=="Year")]
        keep_baskets = [x for x in baskets_lst if x not in drop_baskets]
        frame1 = frame[keep_baskets]
        sum_year = frame1.sum()
        sum_year.name = "PnL"
        sum_year = sum_year.sort_values()
        sort_baskets = sum_year.index.tolist()
        sort_baskets_lst = sort_baskets[::-1]
        sort_baskets_lst1 = sort_baskets_lst[:5]
        self.frame1 = frame1
        self.drop_baskets = drop_baskets
        self.keep_baskets = keep_baskets
        self.sort_baskets_lst = sort_baskets_lst
        self.sort_baskets_lst1 = sort_baskets_lst1
        
    def stats(self, basket):
        new_dict = {}
        new_dict["Inception Date"] = self.change_frame[self.sort_baskets_lst1[basket]].first_valid_index()
        new_dict["Inception PnL"] = self.change_frame[self.sort_baskets_lst1[basket]].sum()
        new_dict["Stats For Year"] = self.lst_year
        new_dict["PnL"] = self.frame1[self.sort_baskets_lst1[basket]].sum()
        new_dict["Daily PnL"] = self.frame1[self.sort_baskets_lst1[basket]].mean()
        new_dict["Maximum PnL"] = self.frame1[self.sort_baskets_lst1[basket]].max()
        new_dict["Minimum PnL"] = self.frame1[self.sort_baskets_lst1[basket]].min()
        new_dict["Stdev"] = self.frame1[self.sort_baskets_lst1[basket]].std()
        new_dict["Positive Days"] = win_days(self.frame1, self.sort_baskets_lst1[basket])
        new_dict["Negative Days"] = loss_days(self.frame1, self.sort_baskets_lst1[basket])      
        self.new_dict = new_dict
        
    def inner_tab(self, basket, emoji, rank, tcol1, tcol2, tcol3):
        self.stats(basket=basket)
        with tcol1:
            st.info("YTD Ranking", icon='📌')
            st.metric("YTD Ranking", value=emoji, delta=rank)
            st.info("Stats For The Year", icon='📌')
            st.metric("Stats For The Year", value=int(self.new_dict["Stats For Year"]))
            pnl3 = locale.currency(self.new_dict["Maximum PnL"], grouping=True, symbol=True) 
            st.info("Maximum Daily PnL (YTD)", icon='📌')                     
            st.metric("Maximum Daily PnL (YTD)", value=f"{pnl3}")     
            st.info("Positive Days (YTD)", icon='📌')                     
            st.metric("Positive Days (YTD)", value=f"""{self.new_dict["Positive Days"]} Days""")                           
        with tcol2:
            st.info("Inception PnL", icon='📌')
            pnl = locale.currency(self.new_dict["Inception PnL"], grouping=True,
                                symbol=True)
            pnl1 = locale.currency(self.new_dict["PnL"], grouping=True, symbol=True)
            st.metric("Inception PnL", value=f"{pnl}")
            st.info("YTD PnL", icon='📌')
            st.metric("YTD PnL", value=f"{pnl1}")
            pnl4 = locale.currency(self.new_dict["Minimum PnL"], grouping=True, symbol=True)
            st.info("Minimum Daily PnL (YTD)", icon='📌')                     
            st.metric("Minimum Daily PnL (YTD)", value=f"{pnl4}")    
            st.info("Negative Days (YTD)", icon='📌')                     
            st.metric("Negative Days (YTD)", value=f"""{self.new_dict["Negative Days"]} Days""")                             
        with tcol3:
            st.info("Inception Date", icon='📌')
            st.metric("Inception Date", value=str(self.new_dict["Inception Date"].date()))
            pnl2 = locale.currency(self.new_dict["Daily PnL"], grouping=True, symbol=True)
            st.info("Daily PnL (YTD)", icon='📌')                     
            st.metric("Daily PnL (YTD)", value=f"{pnl2}")
            pnl5 = locale.currency(self.new_dict["Stdev"], grouping=True, symbol=True)
            st.info("Daily Stdev (YTD)", icon='📌')                     
            st.metric("Daily Stdev (YTD)", value=f"{pnl5}")        
        
    def template(self):
        locale.setlocale(locale.LC_ALL, 'en_US')
        locale.override_localeconv = {'n_sign_posn':1}
        tab1, tab2, tab3, tab4, tab5 = st.tabs(self.sort_baskets_lst1)

        # Custom CSS for scrollable grid layout
        st.markdown(
            """
            <style>
            .scrollable-container {
                display: flex;
                overflow-x: scroll;
                overflow-y: scroll;
                white-space: nowrap;
            }
            .scrollable-container > div {
                flex: 0 0 33.3333%;
                max-width: 33.3333%;
                box-sizing: border-box;
                padding: 10px;
                display: inline;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        with tab1:
            tcol1, tcol2, tcol3 = st.columns(3)
            st.column_config.Column(width="large")
            self.inner_tab(0, "⭐⭐⭐⭐⭐", 1, tcol1, tcol2, tcol3)  
        with tab2:
            tcol4, tcol5, tcol6 = st.columns(3)
            self.inner_tab(1, "⭐⭐⭐⭐", 2, tcol4, tcol5, tcol6)
        with tab3:
            tcol7, tcol8, tcol9 = st.columns(3)
            self.inner_tab(2, "⭐⭐⭐", 3, tcol7, tcol8, tcol9)   
        with tab4:
            tcol10, tcol11, tcol12 = st.columns(3)
            self.inner_tab(3, "⭐⭐", 4, tcol10, tcol11, tcol12)
        with tab5:
            tcol13, tcol14, tcol15 = st.columns(3)
            self.inner_tab(4, "⭐", 5, tcol13, tcol14, tcol15)                                           
                                               
                    # Make columns scrollable by setting a fixed height
            
            

    def rerun(self):
        st.rerun()
        
    def timezone(self):
        IST = pytz.timezone("Asia/Kolkata")  
        self.IST = IST  
        
    def check_time(self):
        now_utc = datetime.now(pytz.UTC)
        now_ist = now_utc.astimezone(self.IST)
        if now_ist.hour == 19 and now_ist.minute == 00:
            self.rerun()
            
    def schedule_(self):
        schedule.every().hour.do(self.check_time)
        
    def run_schedule(self):
        while True:
            schedule.run_all()
            time.sleep(1)
            
    def updates(self):
        st.write("Refresh done")
        if "scheduler" not in st.session_state:
            st.session_state.scheduler = self.run_schedule()        
        
    def authenticated_menu(self):
        self.page_config()
        self.connections()
        self.read_data()
        self.create_stats()
        self.template()
       # self.timezone()
       # self.check_time()
       # self.schedule_()
       # self.run_schedule()
       # self.updates() 
    
if __name__ == "__main__":
    home_obj = homepage()
    homepage_display = home_obj.authenticated_menu()
