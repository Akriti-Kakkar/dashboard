import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from stats import *
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import locale
import plotly.express as px
from pages._index_analysis import app
import plotly.graph_objects as go
from colorama import Fore, Style
import sys
from termcolor import colored
from IPython.display import display
import html
from streamlit_extras.metric_cards import style_metric_cards
import ast

class basket_analysis:
    def __init__(self, spreadsheet_name: list, sheet: str) -> None:
        self.spreadsheet_name = spreadsheet_name
        self.sheet = sheet
    
    @staticmethod
    def page_config() -> None:
        st.set_page_config(page_title='Dashboard', page_icon='🌎', initial_sidebar_state="expanded")
        st.sidebar.image('htts_fund_logo.png', caption='HTTS Fund')
        #st.subheader('📈 Baskets Vs S&P Analysis')
        # Inject custom CSS to set the width of the sidebar
        st.markdown("""
            <style> section[data-testid="stSidebar"] { width: 505px !important; }
            </style>
        """, unsafe_allow_html=True)
        
    def get_data(self):
        conn = st.connection("gsheets", type=GSheetsConnection)
        capital_data = conn.read(worksheet=self.spreadsheet_name[0])
        cashflow_data = conn.read(worksheet=self.spreadsheet_name[4])
        change_data = conn.read(worksheet=self.spreadsheet_name[1])
        mtm_data_forex = conn.read(worksheet=self.spreadsheet_name[2])
        mtm_data = conn.read(worksheet=self.spreadsheet_name[3])           
        capital_data = capital_data.set_index('Date')
        capital_data.index = pd.to_datetime(capital_data.index)
        cashflow_data = cashflow_data.set_index('Date')
        cashflow_data.index = pd.to_datetime(cashflow_data.index)
        change_data = change_data.set_index('Date')       
        change_data.index = pd.to_datetime(change_data.index)
        baskets_lst1 = capital_data.columns.tolist()
        baskets_lst1 = baskets_lst1[2:]        
        frame1 = change_data[baskets_lst1]
        sum_year = frame1.sum()
        sum_year.name = "PnL"
        sum_year = sum_year.sort_values()
        sort_baskets = sum_year.index.tolist()
        baskets_lst = sort_baskets[::-1]
        active_baskets1 = [col for col in capital_data.columns if 
                          capital_data[col].isna().iloc[-1]!=True]   
        active_baskets1 = active_baskets1[2:]       
        frame11 = change_data[active_baskets1]
        sum_year1 = frame11.sum()
        sum_year1.name = "PnL"
        sum_year1 = sum_year1.sort_values()
        sort_baskets1 = sum_year1.index.tolist()
        active_baskets = sort_baskets1[::-1]
        mtm_data_forex = mtm_data_forex.set_index('Date')
        mtm_data_forex.index = pd.to_datetime(mtm_data_forex.index)
        mtm_data_forex = mtm_data_forex[baskets_lst]
        mtm_data = mtm_data.set_index('Date')
        mtm_data.index = pd.to_datetime(mtm_data.index)
        mtm_data = mtm_data[baskets_lst]
        
        self.mtm_data = mtm_data
        self.mtm_data_forex = mtm_data_forex
        self.change_data = change_data
        self.cashflow_data = cashflow_data
        self.capital_data = capital_data
        self.baskets_lst = baskets_lst
        self.active_baskets = active_baskets  
        self.conn = conn  
        
    def connect_index(self):
        obj = app(self.sheet)
        obj.get_data()
        obj.calculate_returns()
        index_data = obj.data
        self.index_data = index_data
        
    def placeholder_widgets(self):
        sh = st.empty()
        st_col, en_col, view_col, view1_col = st.columns(4)
        with st_col:
            placeholder_basket = st.empty()
        with en_col:
            placeholder_basket1 = st.empty()
        with view_col:
            placeholder_basket2 = st.empty()
        with view1_col:
            placeholder_basket3 = st.empty()
        
        self.placeholder_basket = placeholder_basket
        self.placeholder_basket1 = placeholder_basket1
        self.placeholder_basket2 = placeholder_basket2
        self.placeholder_basket3 = placeholder_basket3   
        self.st_col = st_col
        self.en_col = en_col
        self.view_col = view_col
        self.view1_col = view1_col
        self.sh = sh
    
    def calc_engine(self):
        cap_data = self.capital_data[self.baskets_lst]
        start_cap = self.capital_data.apply(
            lambda col: col.dropna().iloc[0] if not col.dropna().empty
            else None
        )
        end_cap = self.capital_data.apply(
            lambda col: col.dropna().iloc[-1] if not col.dropna().empty
            else None
        )
        start_cap = start_cap[2:]
        end_cap = end_cap[2:]
        active_capital_data = self.capital_data[self.active_baskets]
        start_cap_active = active_capital_data.apply(
            lambda col: col.dropna().iloc[0] if not col.dropna().empty
            else None
        )
        end_cap_active = active_capital_data.apply(
            lambda col: col.dropna().iloc[-1] if not col.dropna().empty
            else None
        )
        start_date = cap_data.apply(lambda col: col.dropna().index.min().date()
                                             if not col.dropna().empty else None)
        start_date_active = active_capital_data.apply(
           lambda col: col.dropna().index.min().date() if not col.dropna().empty else None
        )
        end_date = cap_data.apply(
            lambda col: col.dropna().index.max().date() if not col.dropna().empty else None
        )
        end_date_active = active_capital_data.apply(lambda col: col.dropna().index.max().date()
                                                    if not col.dropna().empty else None)
        dep = self.cashflow_data[self.baskets_lst]
        dep_sum = dep.sum(axis=0)
        dep_active = self.cashflow_data[self.active_baskets]
        dep_sum_active = dep_active.sum(axis=0) 
        ch = self.change_data[self.baskets_lst]
        ch_sum = ch.sum(axis=0)  
        ch_active = self.change_data[self.active_baskets]
        ch_sum_active = ch_active.sum(axis=0) 
        daily_twr_data = ch / cap_data
        daily_twr_active_data = ch_active / active_capital_data
        result_twr  = daily_twr_data.apply(lambda col: last_n_twr(
            daily_twr_data, col.name, len(daily_twr_data.dropna(subset=col.name)), True
        )) * 100
        result_twr_active  = daily_twr_active_data.apply(lambda col: last_n_twr(
            daily_twr_active_data, col.name, len(daily_twr_active_data.dropna(subset=col.name)), True
        )) * 100        

        result_dict = {}
        for col in cap_data.columns:
            wt_cash, capital = last_n_weighted_cash_flow(
                ch[col], dep[col], cap_data[col]
            )
            result_dict[col] = {'wt_cash': wt_cash, 'capital': capital}
        mwr_lst = []
        for col in cap_data.columns:
            mwr_lst.append(last_n_mwr(result_dict[col]['wt_cash'], 
                                  ch[col], result_dict[col]['capital']))
        
        result_dict_active = {}
        for col1 in active_capital_data:
            wt_cash1, capital1 = last_n_weighted_cash_flow(
                ch_active[col1], dep_active[col1], active_capital_data[col1]
            )
            result_dict_active[col1] = {'wt_cash': wt_cash1, 'capital':capital1}
        mwr_active_lst = []
        for col1 in active_capital_data.columns:
            mwr_active_lst.append(last_n_mwr(result_dict_active[col1]['wt_cash'],
                                         ch_active[col1], 
                                         result_dict_active[col1]['capital']))
            
    
        self.cap_data = cap_data
        self.dep = dep
        self.ch = ch
        self.start_cap = start_cap
        self.active_capital_data = active_capital_data
        self.end_cap = end_cap
        self.end_cap_active = end_cap_active
        self.start_cap_active = start_cap_active
        self.dep_sum = dep_sum
        self.dep_sum_active = dep_sum_active
        self.ch_sum = ch_sum
        self.ch_sum_active = ch_sum_active
        self.start_date = start_date
        self.start_date_active = start_date_active
        self.end_date = end_date
        self.end_date_active = end_date_active
        self.result_twr = result_twr
        self.result_twr_active = result_twr_active
        self.mwr_lst = mwr_lst
        self.mwr_active_lst = mwr_active_lst
     
    def baskets_mwr_page(self, basket, cap_data, ch, dep):
        self.sh = self.sh
        ind1_ = ch[basket].first_valid_index()
        ind_ = ch[basket].last_valid_index()
        ind_data = self.index_data.loc[ind1_:ind_]
        wt_cash_, capital_ = last_n_weighted_cash_flow(
                ch[basket], dep[basket], cap_data[basket]
                )        
        metric_Data = ch[basket].dropna()
        ret_data = metric_Data/capital_
        ret_data1 = ret_data.apply(lambda x:x*100)  
        st_col, en_col, view_col, view1_col = st.columns(4)
        with st_col:
            self.placeholder_basket = self.placeholder_basket
        with en_col:
            self.placeholder_basket1 = self.placeholder_basket1
        with view_col:
            self.placeholder_basket2 = self.placeholder_basket2
        with view1_col:
            self.placeholder_basket3 = self.placeholder_basket3
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info('1D Return', icon='📌')
            try:
                wt_cash, capital = last_n_weighted_cash_flow(
                        pd.Series(ch.loc[ind_, basket]), 
                        pd.Series(dep.loc[ind_, basket]), 
                        pd.Series(cap_data.loc[ind_, basket])
                    )
                ind_ret1 = ind_data.loc[ind_, 'mwr']
                print('ind_ret:', ind_ret1)
                mwr = last_n_mwr(wt_cash, 
                                 pd.Series(ch.loc[ind_, basket]), 
                                 capital)
                st.metric('1D Return', value=f"{mwr*100:.2f}%")
                st.write(f"S&P: {ind_ret1*100:.2f}%")
                an = comparison(mwr, ind_ret1, "normal")
                em_an = comparison_emoji(an)
                st.warning(f"{em_an} Basket {an} S&P")
            except IndexError:
                st.metric('1D Return', value=f'{np.nan}')
                st.write(ch.loc[ch.last_valid_index(), basket])
            try:
                mwr_ = last_n_mwr(wt_cash_, ch[basket], capital_)  
                st.info('Period Return', icon='📌')
                st.metric('Period Return', value=f"{mwr_*100:.2f}%") 
                ind_lst = ind_data.loc[ind_, 'Close']
                ind_fst = ind_data.loc[ind1_, 'Close']
                ind_pnl = ind_lst - ind_fst
                ind_reti = ind_pnl/ind_fst
                st.write(f"S&P: {ind_reti*100:.2f}%")
                an1 = comparison(mwr_, ind_reti, "normal")
                em_an1 = comparison_emoji(an1)
                st.warning(f"{em_an1} Basket {an1} S&P")
            except IndexError:
                st.info('Period Return', icon='📌')
                st.metric('Period Return', value=f'{np.nan}')  
            st.info('Invested Value (Static)', icon='📌')
            try:
                iv = capital_.loc[capital_.index.min()] + dep[basket].sum()
                iv1 = locale.currency(iv, symbol=True, grouping=True)
                st.metric('Invested Value (Static)', value=iv1)         
                st.write('S&P: -')
                st.warning('👍 Investments over the horizon')                
            except:                         
                st.metric('Invested Value (Static)', value=np.nan)                              
            st.info('Positive Days', icon='📌')
            try:
                pos_days = win_days(ch, basket)
                pos_days1 = win_days(ind_data, 'mwr')
                st.metric('Positive Days', value=f"{pos_days} Days")
                st.write(f"S&P: {pos_days1} Days")
                an2 = comparison(pos_days, pos_days1, "normal")
                em_an2 = comparison_emoji(an2)
                st.warning(f"{em_an2} Basket {an2} S&P")
            except:
                st.metric('Positive Days', value=np.nan)
            st.info('Negative Days', icon='📌')
            try:
                neg_days = loss_days(ch, basket)
                neg_days1 = loss_days(ind_data, 'mwr')
                an3 = comparison_alt(neg_days, neg_days1, "normal")
                em_an3 = comparison_emoji(an3)
                st.metric('Negative Days', value=f'{neg_days} Days')
                st.write(f"S&P: {neg_days1} Days")
                st.warning(f"{em_an3} Basket {an3} S&P")
            except:
                st.metric('Negative Days', value=np.nan)
            st.info('Duration', icon='📌')
            try:
                start_date = ch[basket].first_valid_index()
                end_date = ch[basket].last_valid_index()
                du = duration(start_date, end_date)
                du1 = duration(ind1_, ind_)
                an4 = comparison(du, du1, "normal")
                em_an4 = comparison_emoji(an4)
                st.metric('Duration', value=f'{du} Days')
                st.write(f"S&P: {du1} Days")
                st.warning(f"{em_an4} Basket {an4} S&P")
            except:
                st.metric('Duration', value=np.nan)                

        with col2:
            try:
                ind_data21 = ind_data.iloc[-21:]
                ind21_op = ind_data21['Close'].iloc[0]
                ind_21cl = ind_data21['Close'].iloc[-1]
                ind21_pnl = ind_21cl - ind21_op
                ind_mwr21 = ind21_pnl/ind21_op 
            except IndexError:
                ind21_op = ind_data['Close'].iloc[0]
                ind_21cl = ind_data['Close'].iloc[-1]
                ind21_pnl = ind_21cl - ind21_op
                ind_mwr21 = ind21_pnl/ind21_op 
            try:
                wt_cash21, capital21 = last_n_weighted_cash_flow(
                        ch[basket], dep[basket], cap_data[basket],
                        n=21
                        )
                mwr21 = last_n_mwr(wt_cash21, ch[basket], capital21, n=21) 
                an5 = comparison(mwr21, ind_mwr21, "normal")
                em_an5 = comparison_emoji(an5)
                st.info('21D Return', icon='📌')
                st.metric('21D Return', value=f"{mwr21*100:.2f}%") 
                st.write(f"S&P: {ind_mwr21*100:.2f}%")
                st.warning(f"{em_an5} Basket {an5} S&P")
            except IndexError:
                st.info('21D Return', icon='📌')
                st.metric('21D Return', value=f'{np.nan}') 
            try: 
                start_cap = capital_.loc[capital_.index.min()]
                base_cap = start_cap + sum(wt_cash_) 
                base_cap1 = locale.currency(base_cap, symbol=True, grouping=True)                                        
                st.info('Weighted Allocation', icon='📌')
                st.metric('Weighted Allocation', value=base_cap1) 
                st.write(f"S&P: - ")
                st.warning("👍 Initial Cap + Sum Of Wt. Cash Flows")
            except:
                st.metric('Weighted Allocation', value=f'{np.nan}')                  
            positive_pnl = ch.copy()
            positive_pnl = positive_pnl[positive_pnl[basket]>0]
            pos_pnl11 = ind_data.copy()
            pos_pnl11 = pos_pnl11[pos_pnl11['pnl']>0]
            negative_pnl = ch.copy()
            negative_pnl = negative_pnl[negative_pnl[basket]<0]
            neg_pnl11 = ind_data.copy()
            neg_pnl11 = neg_pnl11[neg_pnl11['pnl']<0]
            pos_pnl = sum(positive_pnl[basket])
            pos_pnl1 = locale.currency(pos_pnl, symbol=True, grouping=True)
            ind_pos_pnl = sum(pos_pnl11['pnl'])            
            neg_pnl = sum(negative_pnl[basket])
            neg_pnl1 = locale.currency(neg_pnl, symbol=True, grouping=True)
            ind_neg_pnl = sum(neg_pnl11['pnl'])
            ind_pos_ret = ind_pos_pnl/ind_fst
            ind_neg_ret = ind_neg_pnl/ind_fst
            st.info('Positive PnL', icon='📌')
            st.metric('Positive PnL', value=pos_pnl1) 
            st.write("S&P: - ")
            st.warning("👍 Sum of postive pnl over the horizon")                
            try:
                mwr_pos = pos_pnl / base_cap
                st.info('Positive PnL (%)', icon='📌')
                st.metric('Positive PnL (%)', value=f"{mwr_pos*100:.2f}%") 
                an6 = comparison(mwr_pos, ind_pos_ret, "normal")
                em_an6 = comparison_emoji(an6)
                st.write(f"S&P: {ind_pos_ret*100:.2f}%")
                st.warning(f"{em_an6} Basket {an6} S&P")
            except:
                st.info('Positive PnL (%)', icon='📌')
                st.metric('Positive PnL (%)', value=f'{np.nan}')   
            st.info('CAGR', icon='📌')    
            try:
                end_val = base_cap + ch[basket].sum()                
                co = cagr(base_cap, end_val, du)
                co1 = cagr(ind_fst, ind_lst, du1)
                an7 = comparison(co, co1, "normal")
                em_an7 = comparison_emoji(an7)
                st.metric('CAGR', value = f"{co*100:.2f}%")
                st.write(f"S&P: {co1*100:.2f}%")
                st.warning(f"{em_an7} Basket {an7} S&P")
            except:
                st.metric('CAGR', value=np.nan)   
            st.info('Win-Loss Ratio', icon='📌')    
            try:
                wl_ind = win_loss(pos_days1, neg_days1)
                wl = win_loss(pos_days, neg_days)  
                an8 = comparison(wl, wl_ind, "normal")
                em_an8 = comparison_emoji(an8)
                st.metric('Win-Loss Ratio', value=f"{wl:.2f}")
                st.write(f"S&P: {wl_ind:.2f}")
                st.warning(f"{em_an8} Basket {an8} S&P")
            except:
                st.metric('Win-Loss Ratio', value=np.nan)                
            
        with col3:
            try:
                ind_data60 = ind_data.iloc[-60:]
                ind_fst60 = ind_data60['Close'].iloc[0]
                ind_lst60 = ind_data60['Close'].iloc[-1]
                ind_60pnl = ind_lst60 - ind_fst60
                ind_mwr60 = ind_60pnl/ind_fst60
            except IndexError:
                ind_lst60 = ind_data['Close'].iloc[-1]
                ind_fst60 = ind_data['Close'].iloc[0]
                ind_60pnl = ind_lst60 - ind_fst60
                ind_mwr60 =  ind_60pnl/ind_fst60 
            try:
                wt_cash60, capital60 = last_n_weighted_cash_flow(
                        ch[basket], dep[basket], cap_data[basket],
                        n=60
                        )
                mwr60 = last_n_mwr(wt_cash60, ch[basket], capital60,
                                   n=60)  
                an9 = comparison(mwr60, ind_mwr60, "normal")
                em_an9 = comparison_emoji(an9)
                st.info('60D Return', icon='📌')
                st.metric('60D Return', value=f"{mwr60*100:.2f}%") 
                st.write(f"S&P: {ind_mwr60*100:.2f}%")
                st.warning(f"{em_an9} Basket {an9} S&P")
            except IndexError:
                st.info('60D Return', icon='📌')
                st.metric('60D Return', value=f'{np.nan}')   
            st.info('Weighted Ending Value', icon='📌')
            try:
                end_val1 = locale.currency(end_val, symbol=True, grouping=True)
                st.metric('Weighted Ending Value', value=end_val1)
                st.write("S&P: - ")
                st.warning("👍 Weighted Allocation + PnL")
            except:
                st.metric('Ending Value', value=np.nan)                   
            st.info('Negative PnL', icon='📌')
            st.metric('Negative PnL', value=neg_pnl1)  
            st.write("S&P: - ")
            st_cp = comparison(base_cap1, end_val1, "normal")
            st_em = comparison_emoji(st_cp)
            st.warning(f"{st_em} Sum of negative pnl over the horizon")
            try:
                mwr_neg = neg_pnl / base_cap
                st.info('Negative PnL (%)', icon='📌')
                an10 = comparison(mwr_neg, ind_neg_ret, "normal")
                st.metric('Negative PnL (%)', value=f"{mwr_neg*100:.2f}%") 
                st.write(f"S&P: {ind_neg_ret*100:.2f}%")
                em_an10 = comparison_emoji(an10)
                st.warning(f"{em_an10} Basket {an10} S&P")
            except:
                st.info('Negative PnL (%)', icon='📌')
                st.metric('Negative PnL (%)', value=f'{np.nan}')  
            st.info('PnL', icon='📌')          
            try:
                change = ch[basket].sum()
                change1 = locale.currency(change, symbol=True, grouping=True)
                ind_change = ind_data['pnl'].sum()              
                st.metric('PnL', value=change1)
                st.write("S&P: -")
                st.warning("👍 Sum of profit over the horizon")
            except:
                st.metric('PnL', value=np.nan)
            st.info('Winning Pct', icon='📌')
            try:
                ind_wn = win_pct(pos_days1, du1)
                wn = win_pct(pos_days, du) 
                an11 = comparison(wn, ind_wn, "normal")
                st.metric('Winning Pct', value = f"{wn*100:.2f}%")
                st.write(f"S&P: {ind_wn*100:.2f}%")
                em_an11 = comparison_emoji(an11)
                st.warning(f"{em_an11} Basket {an11} S&P")
            except:
                st.metric('Winning Pct', value=np.nan) 
                       
        ind_data['money_wt'] = ind_data['mwr'].apply(lambda x: x*100)
        fig = px.line(ret_data1, y = basket, x = ret_data1.index,
                        template='plotly_white')
        fig.add_trace(go.Line(x=ind_data.index, y=ind_data['money_wt'], 
                              mode='lines', name='S&P'))        
        fig.update_layout(title = "Discrete View Of Daily Returns",
                          plot_bgcolor="#FFFFFF", 
                            yaxis_title="Daily Money-Weighted Returns (%)",
                            xaxis_title="Date")     
        fig.update_xaxes(linecolor='green', showgrid=False, rangeslider_visible=True,
                                        rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ))
        fig.update_yaxes( linecolor='blue', showgrid=False)  
        fig_place = st.empty()                                
        fig_place.plotly_chart(fig)     
                                            
    def fund_mwr_page(self, change_data, mn_wt, baskets_lst_):
        st.subheader('📈 Baskets Vs S&P Analysis')
        frame = change_data.fillna(0)
        drop_baskets = [x for x in baskets_lst_ if (x.endswith("_unmerged"))|(x.endswith("_removed"))|(x=="Year")]
        keep_baskets = [x for x in baskets_lst_ if x not in drop_baskets]
        #frame = frame.drop([x for x in frame.columns if (x.endswith("_unmerged"))|(x.endswith("_removed"))|(x=="Year")],
        #                   axis=1)
        frame = change_data[keep_baskets]
        st.markdown("<font color='green'><b><span style='font-size: 24px;'>🔝 Top 2 Baskets</span></b></font>", unsafe_allow_html=True)
        fig_fund = px.density_heatmap(frame, x = frame.index, y = frame.columns.tolist()[:2],
                                      facet_col="variable")
        fig_fund.update_layout(title="PnL Density Heatmap Of Top 2 Baskets",
                               xaxis_title="Date",
                               yaxis_title="PnL")
        fig_fund.update_xaxes(showgrid=False, rangeslider_visible=True,
                                        rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ))        
        st.plotly_chart(fig_fund, use_container_width=True)
        frame['Date'] = frame.index.to_series()
        frame["Month"] = frame['Date'].dt.strftime("%b%Y")
        fig_fund1 = px.histogram(frame, x = 'Month', y = frame.columns.tolist()[:5])   
        fig_fund1.update_layout(title="MOM PnL Of Top 5 Baskets",
                               xaxis_title="Month",
                               yaxis_title="PnL")
        fig_fund1.update_xaxes(showgrid=False, rangeslider_visible=True)              
        st.plotly_chart(fig_fund1)  
        green = [{'selector': 'th', 'props': '''background-color: #1d4e89; color:#FFFFFF;
            font-weight:bold'''}, {'selector': 'td', 'props': '''text-align: right;
            font-weight:bold, content: attr(data-value);'''}]
        frame = frame.drop(['Date', 'Month'], axis=1)
        frame["Year"] = frame.index.year
        lst_yr = frame["Year"].max()
        sum_year_frame = frame[frame["Year"]==lst_yr]
        sum_year_frame = sum_year_frame.drop("Year", axis=1)
        sum_year = sum_year_frame.sum(axis=0).sum()
        met_pl = st.empty()
        met_pl1 = st.empty()
        st.info(f"{lst_yr} PnL", icon="💲")
        inc1 = locale.currency(sum_year, symbol=True, grouping=True)
        st.metric(label=f"{lst_yr} PnL",
                       value=inc1)    
        frame1 = frame.drop("Year", axis=1)    
        sum_frame = frame1.sum(axis=0).sort_values(ascending=False)
        sum_frame_data = pd.DataFrame(sum_frame, columns=["PnL"])
        inc = locale.currency(sum_frame.sum(), symbol=True, grouping=True)
        met_pl.info("Total PnL", icon="💲")
        met_pl1.metric(label="Total PnL",
                       value=inc)
        sum_frame_data['Baskets'] = sum_frame_data.index
        sum_frame_data = sum_frame_data.reset_index(drop=True)
        sum_frame_data.index = sum_frame_data.index+1
        sum_frame_data.index.name = "Rank"
        sum_frame_data = sum_frame_data[["Baskets", "PnL"]]
        sum_frame_data['PnL'] = sum_frame_data['PnL'].apply(
            lambda x: locale.currency(x, symbol=True, grouping=True)) 
        sum_frame_data = sum_frame_data.style.applymap(color_kwargs, subset=["PnL"]
                                             ).set_properties(**{'text-align': 'right'}
                                                              ).set_table_styles(
                green, axis=1).set_caption("Baskets Rankings Based On PnL")
        mwr_frame = pd.DataFrame({'Baskets': baskets_lst_, 'MWR (%)': mn_wt})
        mwr_frame = mwr_frame[~mwr_frame["Baskets"].str.endswith("_unmerged")]
        mwr_frame = mwr_frame[~mwr_frame["Baskets"].str.endswith("_removed")]
        mwr_frame = mwr_frame.sort_values(by='MWR (%)', ascending=False)
        mwr_frame = mwr_frame.reset_index(drop=True)
        mwr_frame['MWR (%)'] = mwr_frame['MWR (%)'].astype(float)
        mwr_frame['Rank'] = mwr_frame.index+1
        mwr_frame = mwr_frame.set_index("Rank")
        mwr_frame = mwr_frame.style.applymap(
            color_code_kwarg, subset=["MWR (%)"]).set_table_styles(green, axis=1).set_properties(
            text_align='right', subset=["MWR (%)"]
        ).format("{:.2%}", subset=["MWR (%)"]).set_caption("Baskets Rankings Based On Returns")     
        
                                             
                                                              
        st.markdown("<font color='green'><b><span style='font-size: 24px;'>🔝 Baskets Rankings</span></b></font>", unsafe_allow_html=True)
        fund_col1, fund_col2 = st.columns(2)
        with fund_col1:
            st.markdown("<font color='green'><b><span style='font-size: 24px;'>🔝 Rankings Based On PnL</span></b></font>", unsafe_allow_html=True)
            #st.table(sum_frame_data)
            st.dataframe(sum_frame_data)
        with fund_col2:
            st.markdown("<font color='green'><b><span style='font-size: 24px;'>🔝 Rankings Based On Returns</span></b></font>", unsafe_allow_html=True)
            st.table(mwr_frame)
            
    def baskets_twr_page(self, basket, cap_data, ch, dep):
        self.sh = self.sh
        green = [{'selector': 'th', 'props': '''background-color: #1d4e89; color:#FFFFFF;
            font-weight:bold'''}, {'selector': 'td', 'props': '''text-align: right;
            font-weight:bold'''}]
        red = [{'selector': 'th', 'props': 'background-color: red'}]
        ret_twr_data = pd.DataFrame(columns=['returns', 'ec'])
        ret_twr_data['returns'] = ch[basket]/cap_data[basket]
        start = ch.index.min().date()
        end = ch.index.max().date()
        allocation = cap_data.loc[pd.to_datetime(start), basket]
        ind_data_twr = self.index_data[start:end]
        ret_twr_data['ec'] = (1 + ret_twr_data['returns']).cumprod() * allocation  
        ind_data_twr['ec'] = (1 + ind_data_twr['returns']).cumprod() * allocation     
        st.table(pd.DataFrame({'Starting Date': [start], 'Latest Ending Date': [end]},
                                  index=['TimeStamps']).style.set_table_styles(green, axis=1))
        mwr_placeholder100 = st.empty()
        mwr_placeholder10 = st.empty()
        mwr_placeholder_col1 = st.empty()
        st.subheader('Detailed Risk Analysis')
        mwr_placeholder = st.empty()
        mwr_placeholder1 = st.empty()
        st.subheader('Detailed Risk Return Analysis')
        mwr_placeholder2 = st.empty()
        mwr_placeholder3 = st.empty()     
        fig = px.line(ret_twr_data, y = 'ec', x = ret_twr_data.index,
                        template='plotly_white', width=1000)
        fig.add_trace(go.Line(x=ind_data_twr.index, y=ind_data_twr['ec'], 
                            mode='lines', name='S&P'))              
        fig.update_layout(title = "Continuous Equity Curve",
                          plot_bgcolor="#FFFFFF", 
                            yaxis_title="Equity Curve ($)",
                            xaxis_title="Date")  
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        mwr_placeholder100.plotly_chart(fig)  

        active = duration(start, end)
        mwr_comp1 = comparison(active, active, "normal")
        mwr_em = comparison_emoji(mwr_comp1)
        end_all = ret_twr_data.loc[ret_twr_data.index[-1], 'ec']
        end_all_ind = ind_data_twr.loc[ind_data_twr.index[-1], 'ec']
        mwr_comp2 = comparison(end_all, end_all_ind, "normal")
        mwr_em2 = comparison_emoji(mwr_comp2)
        ret = cagr(allocation, end_all, active)
        ret_ind = cagr(allocation, end_all_ind, active)
        mwr_comp3 = comparison(ret, ret_ind, "normal")
        mwr_em3 = comparison_emoji(mwr_comp3)
        mn_ret = mu(ret_twr_data, 'returns')
        mn_ret_ind = mu(ind_data_twr, 'returns')
        mwr_comp4 = comparison(mn_ret, mn_ret_ind, "normal")
        mwr_em4 = comparison_emoji(mwr_comp4)
        stde = stdev(ret_twr_data, 'returns')
        stde_ind = stdev(ind_data_twr, 'returns')
        mwr_comp5 = comparison(stde, stde_ind, "risk")
        mwr_em5 = comparison_emoji(mwr_comp5) 
        ann_vol = annualized_vol(stde)
        ann_vol_ind = annualized_vol(stde_ind)
        mwr_comp6 = comparison(ann_vol, ann_vol_ind, "risk")
        mwr_em6 = comparison_emoji(mwr_comp6)
        shp = sharpe_ratio(ret, ann_vol)
        shp_ind = sharpe_ratio(ret_ind, ann_vol_ind)
        mwr_comp7 = comparison(shp, shp_ind, "normal")
        mwr_em7 = comparison_emoji(mwr_comp7)
        dd = drawdown(ret_twr_data, 'ec')
        dd_ind = drawdown(ind_data_twr, 'ec')
        mdd = max_drawdown(dd)
        mdd_ind = max_drawdown(dd_ind)
        mwr_comp9 = comparison_alt(mdd, mdd_ind, "risk")
        mwr_em9 = comparison_emoji(mwr_comp9)
        ad = avg_drawdown(dd) 
        ad_ind = avg_drawdown(dd_ind)
        mwr_comp10 = comparison_alt(ad, ad_ind, "risk")
        mwr_em10 = comparison_emoji(mwr_comp10)
        wn_d = win_days(ret_twr_data, 'returns')
        wn_d_ind = win_days(ind_data_twr, 'returns')
        mwr_comp11 = comparison(wn_d, wn_d_ind, "normal")
        mwr_em11 = comparison_emoji(mwr_comp11)
        ln_d = loss_days(ret_twr_data, 'returns')
        ln_d_ind = loss_days(ind_data_twr, 'returns')
        mwr_comp12 = comparison_alt(ln_d, ln_d_ind, "normal")
        mwr_em12 = comparison_emoji(mwr_comp12)
        wn = win_pct(wn_d, active)
        wn_ind = win_pct(wn_d_ind, active)
        mwr_comp8 = comparison(wn, wn_ind, "normal")
        mwr_em8 = comparison_emoji(mwr_comp8)
        wl = win_loss(wn_d, ln_d)
        wl_ind = win_loss(wn_d_ind, ln_d_ind)
        mwr_comp13 = comparison(wl, wl_ind, "normal")
        mwr_em13 = comparison_emoji(mwr_comp13)
        dow = downside_deviation(ret_twr_data, 'returns')
        dow_ind = downside_deviation(ind_data_twr, 'returns')
        mwr_comp14 = comparison_alt(dow, dow_ind, "risk")
        mwr_em14 = comparison_emoji(mwr_comp14)
        sort1 = sortino_ratio(ret, dow)
        sort1_ind = sortino_ratio(ret_ind, dow_ind)
        mwr_comp15 = comparison(sort1, sort1_ind, "normal")
        mwr_em15 = comparison_emoji(mwr_comp15)
        max_cons_pos = getMaxLength(ret_twr_data['returns'], 1)
        max_cons_pos_ind = getMaxLength(ind_data_twr['returns'], 1)
        mwr_comp16 = comparison(max_cons_pos, max_cons_pos_ind, "normal")
        mwr_em16 = comparison_emoji(mwr_comp16)
        max_cons_neg = getMaxLength(ret_twr_data['returns'], 0)
        max_cons_neg_ind = getMaxLength(ind_data_twr['returns'], 0)
        mwr_comp17 = comparison_alt(max_cons_neg, max_cons_neg_ind, "normal")
        mwr_em17 = comparison_emoji(mwr_comp17)
        m_ret = avg_monthly_twr(ret_twr_data, 'returns')
        m_ret_ind = avg_monthly_twr(ind_data_twr, 'returns')
        mwr_comp18 = comparison(m_ret, m_ret_ind, "normal")
        mwr_em18 = comparison_emoji(mwr_comp18)
        one_ret = last_n_twr(ret_twr_data, 'returns', 252, False)
        one_ret_ind = last_n_twr(ind_data_twr, 'returns', 252, False)
        mwr_comp19 = comparison(one_ret, one_ret_ind, "normal")
        mwr_em19 = comparison_emoji(mwr_comp19)
        od_ret = last_n_twr(ret_twr_data, 'returns', 1, False)
        od_ret_ind = last_n_twr(ind_data_twr, 'returns', 1, False)
        mwr_comp20 = comparison(od_ret, od_ret_ind, "normal")
        mwr_em20 = comparison_emoji(mwr_comp20)
        t1d_ret = last_n_twr(ret_twr_data, 'returns', 21, False)
        t1d_ret_ind = last_n_twr(ind_data_twr, 'returns', 21, False)
        mwr_comp21 = comparison(t1d_ret, t1d_ret_ind, "normal") 
        mwr_em21 = comparison_emoji(mwr_comp21)           
        s0d_ret = last_n_twr(ret_twr_data, 'returns', 60, False)
        s0d_ret_ind = last_n_twr(ind_data_twr, 'returns', 60, False)
        mwr_comp22 = comparison(s0d_ret, s0d_ret_ind, "normal")
        mwr_em22 = comparison_emoji(mwr_comp22)
        dep_ = dep[basket].sum()
        dep_ind = 0
        beta_st = beta(ret_twr_data['returns'], ind_data_twr['returns'])
        beta_in = 1
        mwr_comp23 = comparison(beta_st, beta_in, "risk")
        mwr_em23 = comparison_emoji(mwr_comp23)
        tr = treynor_ratio(ret, beta_st)
        tr_in = treynor_ratio(ret_ind, beta_in)
        mwr_comp24 = comparison(tr, tr_in, "normal")
        mwr_em24 = comparison_emoji(mwr_comp24)
        alpha_st = alpha(ret, ret_ind)
        alpha_in = alpha(ret_ind, ret_ind)
        mwr_comp25 = comparison(alpha_st, alpha_in, "normal")
        mwr_em25 = comparison_emoji(mwr_comp25)
        er = required_return(beta_st, ret_ind)
        er_in = required_return(beta_in, ret_ind)
        mwr_comp26 = comparison(er, er_in, "performance")
        mwr_em26 = comparison_emoji(mwr_comp26)
        aj = jenson_alpha(ret, er)
        aj_in =jenson_alpha(ret_ind, er_in)
        mwr_comp27 = comparison(aj, aj_in, "normal")
        mwr_em27 = comparison_emoji(mwr_comp27)
        mwr_comp_dep = comparison(dep_, 0, "deposits")
        mwr_em_dep = comparison_emoji(mwr_comp_dep)
            
        stats_data = pd.DataFrame({
            'Stats' : ['Duration',
                        'Starting Value', 'Deposits/Withdrawals',
                        'Ending Value', 'Mean Return', 
                        'Average Monthly Return',
                        'Last 12 Months Return', 'Stdev',
                        'CAGR', 'Annualized Volatility',
                        'Sharpe Ratio', 'Sortino Ratio', 
                        'Average Drawdown', 'Maximum Drawdown',
                        'Winning Pct', 'Win-Loss Ratio',
                        'Max Consecutive Positive Days',
                        'Max Consecutive Negative Days',
                        'Beta', 'Treynor Ratio', 'Alpha',
                        'Required Return', 'Jenson Alpha'],
            
            basket : [f"{active} Days", f"${allocation:,.2f}", f"${dep_:,.2f}", 
                        f"${end_all:,.2f}", f"{mn_ret*100:,.2f}%",
                        f"{m_ret*100:,.2f}%", f"{one_ret*100:,.2f}%",
                        f"{stde*100:,.2f}%",
                        f"{ret*100:,.2f}%", f"{ann_vol*100:,.2f}%", f"{shp:,.2f}",
                        f"{sort1:,.2f}", f"{ad*100:,.2f}%", f"{mdd*100:,.2f}%", f"{wn*100:,.2f}%",
                        f"{wl:,.2f}", max_cons_pos, max_cons_neg, f"{beta_st:.2f}",
                        f"{tr:.2f}", f"{alpha_st*100:.2f}%", f"{er*100:.2f}%",
                        f"{aj:.2f}"],
            
            "S&P": [f"{active} Days", f"${allocation:,.2f}", f"${0:,.2f}", 
                        f"${end_all_ind:,.2f}", f"{mn_ret_ind*100:,.2f}%",
                        f"{m_ret_ind*100:,.2f}%", f"{one_ret_ind*100:,.2f}%",
                        f"{stde_ind*100:,.2f}%",
                        f"{ret_ind*100:,.2f}%", f"{ann_vol_ind*100:,.2f}%", f"{shp_ind:,.2f}",
                        f"{sort1_ind:,.2f}", f"{ad_ind*100:,.2f}%", f"{mdd_ind*100:,.2f}%", 
                        f"{wn_ind*100:,.2f}%", f"{wl_ind:,.2f}", max_cons_pos_ind, max_cons_neg_ind,
                        f"{beta_in:.2f}", f"{tr_in:.2f}", f"{alpha_in*100}%", f"{er_in*100:.2f}%",
                        f"{aj_in:.2f}"] ,
            
            "Comparative Performance": [f"{mwr_comp1}", f"{mwr_comp1}", f"{mwr_comp_dep}", f"{mwr_comp2}", 
                                        f"{mwr_comp4}", f"{mwr_comp18}", f"{mwr_comp19}", f"{mwr_comp5}", 
                                        f"{mwr_comp3}", f"{mwr_comp6}", f"{mwr_comp7}", f"{mwr_comp15}", 
                                        f"{mwr_comp10}", f"{mwr_comp9}", f"{mwr_comp8}", f"{mwr_comp13}",
                                        f"{mwr_comp16}", f"{mwr_comp17}", f"{mwr_comp23}", f"{mwr_comp24}",
                                        f"{mwr_comp25}", f"{mwr_comp26}",
                                        f"{mwr_comp27}"] ,
            
            "Sentiment Vote": [f"{mwr_em}",  f"{mwr_em}", f"{mwr_em_dep}", f"{mwr_em2}", f"{mwr_em4}", 
                               f"{mwr_em18}", f"{mwr_em19}", f"{mwr_em5}", f"{mwr_em3}", f"{mwr_em6}", 
                               f"{mwr_em7}", f"{mwr_em15}", f"{mwr_em10}", f"{mwr_em9}", f"{mwr_em8}", 
                               f"{mwr_em13}", f"{mwr_em16}", f"{mwr_em17}", f"{mwr_em23}", f"{mwr_em24}", 
                               f"{mwr_em25}", f"{mwr_em26}", f"{mwr_em27}"]                                                      
        })
        stats_data.index = stats_data.index + 1
        stats_data = stats_data.style.set_table_styles(green, axis=1)
        mwr_placeholder10.table(stats_data)
        stats_data_risk = pd.DataFrame({'Downside Deviation': [dow, dow_ind], 
                                        'Average Drawdown': [ad, ad_ind],
                                        'Maximum Drawdown': [mdd, mdd_ind]},
                                        index=[['Risk Analysis', 'Risk Analysis'],[basket, 'S&P']])
        stats_data_risk = stats_data_risk.style.set_table_styles(green, axis=1).set_properties(
            text_align='right'
        ).format('{:.2%}')
        mwr_placeholder.table(stats_data_risk)
        dd = pd.DataFrame(dd*100)
        dd = dd.rename(columns = {'ec': 'Drawdown'})
        dd = dd[dd['Drawdown']!=0]
        ind_data_twr_dd = ind_data_twr[ind_data_twr.index.isin(dd.index.to_list())]
        ind_data_twr_dd['returns'] = ind_data_twr_dd['returns'].apply(lambda x: x*100)
        dd['S&P Returns'] = ind_data_twr_dd['returns'].copy()
        dd_ind = pd.DataFrame(dd_ind*100)
        dd_ind = dd_ind.rename(columns = {'ec': 'Drawdown'})
        dd_ind = dd_ind[dd_ind['Drawdown']!=0]
        try:
            fig = px.histogram(dd, y = ['Drawdown', 'S&P Returns'], x = dd.index,
                            template='ggplot2', histfunc='avg')

            fig.update_layout(plot_bgcolor="#FFFFFF", 
                                yaxis_title="Drawdown (%)",
                                xaxis_title="Date",
                                title="Average Of Daily Drawdown Vs Average Of Daily S&P Returns")  
            fig.update_xaxes(linecolor='red', showgrid=False, rangeslider_visible=True,
                                                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ))
            fig.update_yaxes(linecolor='blue', showgrid=False)  
            fig.update_traces(xbins_size="M1")
            fig.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1", tickformat="%b\n%Y")
            fig.update_layout(bargap=0.1)  
        except ValueError:
            dd = dd.fillna(0)
            fig = px.histogram(dd, template='ggplot2', histfunc='avg')
            fig.update_layout(plot_bgcolor="#FFFFFF", 
                                yaxis_title="Drawdown (%)",
                                xaxis_title="Date",
                                title="Average Of Daily Drawdown Vs Average Of Daily S&P Returns")             
            fig.update_yaxes(linecolor='blue', showgrid=False)  
            fig.update_traces(xbins_size="M1")
            fig.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1", tickformat="%b\n%Y")
            fig.update_layout(bargap=0.1)             
                  
        mwr_placeholder1.plotly_chart(fig)              
        stats_data_payoff = pd.DataFrame({'Sharpe Ratio': [shp, shp_ind],
                                            'Sortino Ratio': [sort1, sort1_ind]}, 
                                            index=pd.MultiIndex.from_tuples([('Risk-Return Analysis', basket), ('Risk-Return Analysis', 'S&P')]))
        stats_data_payoff = stats_data_payoff.style.set_table_styles(green, axis=1).set_properties(
            subset=['Sharpe Ratio', 'Sortino Ratio'], text_align='right'
        ).format('{:.2}')
        mwr_placeholder2.table(stats_data_payoff) 
        ret_twr_data['std'] = ret_twr_data['returns'].rolling(window=5).std()
        ret_twr_data['roll_mean'] = ret_twr_data['returns'].rolling(window=5).mean()
        ret_twr_data['roll_sharpe'] = ret_twr_data['roll_mean']/ret_twr_data['std']
        ind_data_twr['std'] = ind_data_twr['returns'].rolling(window=5).std()
        ind_data_twr['roll_mean'] = ind_data_twr['returns'].rolling(window=5).mean()
        ind_data_twr['roll_sharpe'] = ind_data_twr['roll_mean']/ind_data_twr['std']
        fig = px.histogram(ret_twr_data, y = 'roll_sharpe', x = ret_twr_data.index,
                        template='ggplot2', histfunc='avg')
        fig.update_layout(plot_bgcolor="#FFFFFF", 
                            yaxis_title="Sharpe Ratio",
                            xaxis_title="Date",
                            title="Average Of Daily 5-Day Rolling Sharpe Ratio")  
        fig.update_xaxes(linecolor='green', showgrid=False, rangeslider_visible=True,
                                            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ))
        fig.update_yaxes( linecolor='blue', showgrid=False)  
        fig.update_traces(xbins_size="M1")
        fig.update_xaxes(showgrid=True, ticklabelmode="period", dtick="M1", tickformat="%b\n%Y")
        fig.update_layout(bargap=0.1)     
        mwr_placeholder3.plotly_chart(fig)   
        stats_data_ret = pd.DataFrame(data=[[od_ret, 
                                            t1d_ret, 
                                            s0d_ret], 
                                            [od_ret_ind,
                                             t1d_ret_ind,
                                             s0d_ret_ind]],
                                        columns=['Last 1D Ret', 'Last 21D Ret', 'Last 60D Ret'],
                                        index=[basket, 'S&P'])  
        stats_data_ret.index.name = 'Returns (%)'  
        stats_data_ret = stats_data_ret.style.set_table_styles(green, axis=1).set_properties(
            subset=['Last 1D Ret', 'Last 21D Ret', 'Last 60D Ret'], text_align='right'
        ).format('{:.2%}')

        #mwr_placeholder_col1.table(stats_data_ret)  
        mwr_placeholder_col1.table(stats_data_ret)            
        
    def fund_twr_page(self):
        pass
    
    def template(self):
        pass

    def main(self):
        self.page_config()
        self.get_data()
        self.connect_index()
        self.calc_engine()
        self.placeholder_widgets()
        ts = self.cap_data.index.max().year
        text11 = f"Baskets {ts}"
        baskets_radio = st.sidebar.radio('Baskets Selection' ,
                                         options=['Active Baskets', text11], horizontal=True)      
        button1 = st.sidebar.button('Exit View')
        if st.session_state.get('button') != True:
            st.session_state['button'] = button1
                
        
        def func(basket, cap, deposit, endcap, change, start, end_date, twr,
                 mwr, cap_data, change_data, deposit_data, mtm_data_forex,
                 mtm_data, pl, pl1, pl2, pl3, pl_col, pl_col1, pl_col2, pl_col3,
                 head): 
            for x, y, z, l, a, b, c, d, e in list(zip(basket, cap, deposit, endcap, change, start, end_date,
                                                twr, mwr)):   
                if st.session_state[f"{x}"] == True:
                    lst1 = [w for w in basket]
                    lst1.remove(x)
                    print(basket)
                    print(cap)
                    if any((st.session_state[f"{key}"] == True) for key in lst1):
                        st.write('''Click on 'Exit View' before switching between views.''')
                        break
                    else:
                        head.subheader(f"📈 {x} Vs S&P Analysis")
                        ind1 = change_data[x].first_valid_index()
                        indl = change_data[x].last_valid_index()
                        with pl_col:
                            start_ = pl.date_input('Start Date', ind1.date(), min_value=ind1, max_value=indl)
                        with pl_col1:
                            end_ = pl1.date_input('End Date', indl.date(), min_value=ind1, max_value=indl)
                        with pl_col2:
                            locals()[f"{x}_inbut"] = pl2.button("Last 60 Days") 
                            locals()[f"{x}_inbut1"] = pl3.button("Last 21 Days")  
                        with pl_col3:
                            locals()[f"{x}_inbut2"] = st.button("Exit Button")                         
                            
                        # Add css to make text bigger
                        st.markdown(
                            """
                            <style>
                            textarea {
                                font-size: 2rem !important;
                            }
                            input {
                                font-size: 1.5rem !important;
                            }                      
                            </style>
                            """,
                            unsafe_allow_html=True,
                        )   
                        cap_data = cap_data[start_:end_]
                        change_data = change_data[start_:end_]
                        deposit_data = deposit_data[start_:end_]
                        mtm_data = mtm_data[start_:end_]
                        mtm_data_forex = mtm_data_forex[start_:end_]                        
                        locals()[f"{x}_stats"] = st.radio('Choose Type Of Stats', ('MWR', 'TWR'), key=f'{x,y}',
                                                          horizontal=True,
                                                            help='''
                                                            Money Weighted Returns (Modified Dietz Method): 
                                                            Ending Value - Initial Value - Cash Flow/Initial Value + Weighted Cash Flow
                                                            
                                                            Time Weighted Returns (Compounded Returns):
                                                            [(1 + RN) * (1 + RN) * ... -1] * 100
                                                            
                                                            where,
                                                            RN = Ending Value/(Initial Value + Cash Flow)-1 
                                                            '''                                                          )
                        locals()[f"{x}_stats1"] = st.radio('Choose PnL Basis', ('Change', 'MTM', 'MTM (Exc. Forex)'),
                                                           horizontal=True, help='''
                        
                        Change = mark-to-market valuations of assets including forex - 
                        cost (commision, interest, taxes, etc) +
                        dividend - accruals charges + accrual income - basket-level charges +
                        basket-level income
                        
                        MTM = mark-to-market valuations of assets including forex - 
                        cost (commision, interest, taxes, etc) +
                        dividend
                        
                        MTM (Exc. Forex) = mark-to-market valuations of assets excluding forex - 
                        cost (commision, interest, taxes, etc) +
                        dividend''')                                          
                        if locals()[f"{x}_stats"] == 'MWR':
                            if locals()[f"{x}_stats1"] == 'Change':
                                if st.session_state.get(f"button60") != True:
                                    st.session_state["button60"] = locals()[f"{x}_inbut"]  
                                if st.session_state.get("button21") != True:
                                    st.session_state["button21"] = locals()[f"{x}_inbut1"]  
                                if st.session_state.get("exit") != True:
                                    st.session_state["exit"] = locals()[f"{x}_inbut2"]  
                                if st.session_state["exit"] == True:
                                    st.session_state["button60"] = False
                                    st.session_state["button21"] = False
                                    st.session_state["exit"] = False                                                                    
                                if (st.session_state["button60"]==True) and (st.session_state["button21"]==True):
                                    st.warning("Click on exit button before switching between views")
                                  #  st.session_state["exit"] = True
                                elif st.session_state["button60"] == True:
                                    st.session_state["button21"] = False
                                    st.success(f"""You are viewing 60-Day duration MWR stats based 
                                               on change amounts for {x} that started on {b}""")
                                    cap_data1 = cap_data.iloc[-60:]
                                    change_data1 = change_data.iloc[-60:]
                                    deposit_data1 = deposit_data.iloc[-60:]
                                    self.baskets_mwr_page(x, cap_data1, change_data1, deposit_data1)
                                elif st.session_state["button21"] == True:
                                    st.session_state["button60"] = False
                                    st.success(f"""You are viewing 21-Day duration MWR stats based 
                                               on change amounts for {x} that started on {b}""")                                    
                                    cap_data2 = cap_data.iloc[-21:]
                                    change_data2 = change_data.iloc[-21:]
                                    deposit_data2 = deposit_data.iloc[-21:]
                                    self.baskets_mwr_page(x, cap_data2, change_data2, deposit_data2)                                    
                                elif (st.session_state["button60"]!=True) and (st.session_state["button21"]!=True):
                                    st.success(f"""You are viewing MWR stats based 
                                               on change amounts for {x} that started on {b}""")
                                    self.baskets_mwr_page(x, cap_data, change_data, deposit_data)
                            elif locals()[f"{x}_stats1"] == 'MTM':
                                if st.session_state.get(f"button60") != True:
                                    st.session_state["button60"] = locals()[f"{x}_inbut"]  
                                if st.session_state.get("button21") != True:
                                    st.session_state["button21"] = locals()[f"{x}_inbut1"]  
                                if st.session_state.get("exit") != True:
                                    st.session_state["exit"] = locals()[f"{x}_inbut2"]                                  
                                if st.session_state["exit"] == True:
                                    st.session_state["button60"] = False
                                    st.session_state["button21"] = False
                                    st.session_state["exit"] = False  
                                if (st.session_state["button60"]==True) and (st.session_state["button21"]==True):
                                    st.warning("Click on exit button before switching between views")
                                elif st.session_state["button60"] == True:
                                    st.session_state["button21"] = False
                                    st.success(f"""You are viewing 60-Day duration MWR stats based 
                                               on mtm amounts for {x} that started on {b}""")                                    
                                    cap_data3 = cap_data.iloc[-60:]
                                    mtm_data_forex3 = mtm_data_forex.iloc[-60:]
                                    deposit_data3 = deposit_data.iloc[-60:]                                
                                    self.baskets_mwr_page(x, cap_data3, mtm_data_forex3, deposit_data3)
                                elif st.session_state["button21"] == True:
                                    st.session_state["button60"] = False
                                    st.success(f"""You are viewing 21-Day duration MWR stats based 
                                               on mtm amounts for {x} that started on {b}""")                                     
                                    cap_data4 = cap_data.iloc[-21:]
                                    mtm_data_forex4 = mtm_data_forex.iloc[-21:]
                                    deposit_data4 = deposit_data.iloc[-21:]   
                                    self.baskets_mwr_page(x, cap_data4, mtm_data_forex4, deposit_data4)
                                elif (st.session_state["button60"]!=True) and (st.session_state["button21"]!=True):                                 
                                    st.success(f"""You are viewing MWR stats based 
                                               on mtm amounts for {x} that started on {b}""")                                     
                                    self.baskets_mwr_page(x, cap_data, mtm_data_forex, deposit_data)
                            elif locals()[f"{x}_stats1"] == 'MTM (Exc. Forex)':
                                if st.session_state.get(f"button60") != True:
                                    st.session_state["button60"] = locals()[f"{x}_inbut"]  
                                if st.session_state.get("button21") != True:
                                    st.session_state["button21"] = locals()[f"{x}_inbut1"]  
                                if st.session_state.get("exit") != True:
                                    st.session_state["exit"] = locals()[f"{x}_inbut2"]                                  
                                if st.session_state["exit"] == True:
                                    st.session_state["button60"] = False
                                    st.session_state["button21"] = False
                                    st.session_state["exit"] = False   
                                if (st.session_state["button60"]==True) and (st.session_state["button21"]==True):
                                    st.warning("Click on exit button before switching between views")
                                elif st.session_state["button60"] == True:
                                    st.session_state["button21"] = False
                                    st.success(f"""You are viewing 60-Day duration MWR stats based 
                                               on mtm (exc. forex) amounts for {x} that started on {b}""")                                     
                                    cap_data5 = cap_data.iloc[-60:]
                                    mtm_data5 = mtm_data.iloc[-60:]
                                    deposit_data5 = deposit_data.iloc[-60:]
                                    self.baskets_mwr_page(x, cap_data5, mtm_data5, deposit_data5)  
                                elif st.session_state["button21"] == True:
                                    st.session_state["button60"] = False
                                    st.success(f"""You are viewing 21-Day duration MWR stats based 
                                               on mtm (exc. forex) amounts for {x} that started on {b}""")                                      
                                    cap_data6 = cap_data.iloc[-21:]
                                    mtm_data6 = mtm_data.iloc[-21:]
                                    deposit_data6 = deposit_data.iloc[-21:]     
                                    self.baskets_mwr_page(x, cap_data6, mtm_data6, deposit_data6)
                                elif (st.session_state["button60"]!=True) and (st.session_state["button21"]!=True):                                                                   
                                    st.success(f"""You are viewing MWR stats based 
                                               on mtm (exc. forex) amounts for {x} that started on {b}""")                                      
                                    self.baskets_mwr_page(x, cap_data, mtm_data, deposit_data)
                        elif locals()[f'{x}_stats'] == 'TWR':
                            if locals()[f"{x}_stats1"] == 'Change':
                                if st.session_state.get(f"button60") != True:
                                    st.session_state["button60"] = locals()[f"{x}_inbut"]  
                                if st.session_state.get("button21") != True:
                                    st.session_state["button21"] = locals()[f"{x}_inbut1"]  
                                if st.session_state.get("exit") != True:
                                    st.session_state["exit"] = locals()[f"{x}_inbut2"]                                   
                                if st.session_state["exit"] == True:
                                    st.session_state["button60"] = False
                                    st.session_state["button21"] = False
                                    st.session_state["exit"] = False   
                                if (st.session_state["button60"]==True) and (st.session_state["button21"]==True):
                                    st.warning("Click on exit button before switching between views")
                                elif st.session_state["button60"] == True:
                                    st.session_state["button21"] = False
                                    st.success(f"""You are viewing 60-Day duration TWR stats based 
                                               on change amounts for {x} that started on {b}""")                                      
                                    cap_data7 = cap_data.iloc[-60:]
                                    change_data7 = change_data.iloc[-60:]
                                    deposit_data7 = deposit_data.iloc[-60:]
                                    self.baskets_twr_page(x, cap_data7, change_data7, deposit_data7) 
                                elif st.session_state["button21"] == True:
                                    st.session_state["button60"] = False
                                    st.success(f"""You are viewing 21-Day duration TWR stats based 
                                               on change amounts for {x} that started on {b}""")                                       
                                    cap_data8 = cap_data.iloc[-21:]
                                    change_data8 = change_data.iloc[-21:]
                                    deposit_data8 = deposit_data.iloc[-21:]     
                                    self.baskets_twr_page(x, cap_data8, change_data8, deposit_data8) 
                                elif (st.session_state["button60"]!=True) and (st.session_state["button21"]!=True):                               
                                    st.success(f"""You are viewing TWR stats based 
                                               on change amounts for {x} that started on {b}""")                                       
                                    self.baskets_twr_page(x, cap_data, change_data, deposit_data)
                            if locals()[f"{x}_stats1"] == 'MTM':
                                if st.session_state.get(f"button60") != True:
                                    st.session_state["button60"] = locals()[f"{x}_inbut"]  
                                if st.session_state.get("button21") != True:
                                    st.session_state["button21"] = locals()[f"{x}_inbut1"]  
                                if st.session_state.get("exit") != True:
                                    st.session_state["exit"] = locals()[f"{x}_inbut2"]                                   
                                if st.session_state["exit"] == True:
                                    st.session_state["button60"] = False
                                    st.session_state["button21"] = False
                                    st.session_state["exit"] = False   
                                if (st.session_state["button60"]==True) and (st.session_state["button21"]==True):
                                    st.warning("Click on exit button before switching between views")
                                elif st.session_state["button60"] == True:
                                    st.session_state["button21"] = False
                                    st.success(f"""You are viewing 60-Day duration TWR stats based 
                                               on mtm amounts for {x} that started on {b}""")                                       
                                    cap_data9 = cap_data.iloc[-60:]
                                    mtm_data_forex9 = mtm_data_forex.iloc[-60:]
                                    deposit_data9 = deposit_data.iloc[-60:]
                                    self.baskets_twr_page(x, cap_data9, mtm_data_forex9, deposit_data9) 
                                elif st.session_state["button21"] == True:
                                    st.session_state["button60"] = False
                                    st.success(f"""You are viewing 21-Day duration TWR stats based 
                                               on mtm amounts for {x} that started on {b}""")                                      
                                    cap_data10 = cap_data.iloc[-21:]
                                    mtm_data_forex10 = mtm_data_forex.iloc[-21:]
                                    deposit_data10 = deposit_data.iloc[-21:]     
                                    self.baskets_twr_page(x, cap_data10, mtm_data_forex10, deposit_data10) 
                                elif (st.session_state["button60"]!=True) and (st.session_state["button21"]!=True):                                
                                    st.success(f"""You are viewing TWR stats based 
                                               on mtm amounts for {x} that started on {b}""")                                      
                                    self.baskets_twr_page(x, cap_data, mtm_data_forex, deposit_data)    
                            if locals()[f"{x}_stats1"] == 'MTM (Exc. Forex)':
                                if st.session_state.get(f"button60") != True:
                                    st.session_state["button60"] = locals()[f"{x}_inbut"]  
                                if st.session_state.get("button21") != True:
                                    st.session_state["button21"] = locals()[f"{x}_inbut1"]  
                                if st.session_state.get("exit") != True:
                                    st.session_state["exit"] = locals()[f"{x}_inbut2"]                                   
                                if st.session_state["exit"] == True:
                                    st.session_state["button60"] = False
                                    st.session_state["button21"] = False
                                    st.session_state["exit"] = False   
                                if (st.session_state["button60"]==True) and (st.session_state["button21"]==True):
                                    st.warning("Click on exit button before switching between views")
                                elif st.session_state["button60"] == True:
                                    st.session_state["button21"] = False
                                    st.success(f"""You are viewing 60-Day duration TWR stats based 
                                               on mtm (exc. forex) amounts for {x} that started on {b}""")                                      
                                    cap_data11 = cap_data.iloc[-60:]
                                    mtm_data11 = mtm_data.iloc[-60:]
                                    deposit_data11 = deposit_data.iloc[-60:]
                                    self.baskets_twr_page(x, cap_data11, mtm_data11, deposit_data11) 
                                elif st.session_state["button21"] == True:
                                    st.session_state["button60"] = False
                                    st.success(f"""You are viewing 21-Day duration TWR stats based 
                                               on mtm (exc. forex) amounts for {x} that started on {b}""")                                      
                                    cap_data12 = cap_data.iloc[-21:]
                                    mtm_data12 = mtm_data.iloc[-21:]
                                    deposit_data12 = deposit_data.iloc[-21:]     
                                    self.baskets_twr_page(x, cap_data12, mtm_data12, deposit_data12)  
                                elif (st.session_state["button60"]!=True) and (st.session_state["button21"]!=True):                               
                                    st.success(f"""You are viewing TWR stats based 
                                               on mtm (exc. forex) amounts for {x} that started on {b}""")                                      
                                    self.baskets_twr_page(x, cap_data, mtm_data, deposit_data)                                                               
               
                
        if baskets_radio == text11:
            print('Baskets 2024')
            self.baskets = self.baskets_lst
            self.init_cap = self.start_cap
            self.dp = self.dep_sum
            self.end = self.end_cap
            self.change = self.ch_sum
            self.start = self.start_date
            self.end_date = self.end_date
            self.twr = self.result_twr
            self.mwr = self.mwr_lst
            cap_data = self.cap_data
            change_data = self.ch
            deposit_data = self.dep
            mtm_data = self.mtm_data
            mtm_data_forex = self.mtm_data_forex
            pl = self.placeholder_basket
            pl1 = self.placeholder_basket1
            pl2 = self.placeholder_basket2
            pl3 = self.placeholder_basket3
            pl_col = self.st_col
            pl_col1 = self.en_col
            pl_col2 = self.view_col
            pl_col3 = self.view1_col
            head = self.sh
            mn_wt = self.mwr_lst
                                   
            for x, y, z, l, a, b, c, d, e in list(zip(self.baskets, self.init_cap,
                                                self.dp, self.end, self.change, 
                                                self.start, self.end_date,
                                                self.twr, self.mwr)):
                print('init for loop for baskets 2024')
                locale.setlocale(locale.LC_ALL, 'en_US')
                locale.override_localeconv = {'n_sign_posn':1}
                new_val = l+a
                col_change = color_code(a,0) #inception date, end date, invested amount, ending value, change
                col_dep = color_code(z,0) # deposits
                col_twr = color_code(d,0)
                col_mwr = color_code(e,0)
                if col_dep == "red":
                    store_val = "Withdrawals"
                else:
                    store_val = "Deposits"
                if col_twr == "green":
                    emo = "🟢"
                else:
                    emo = "🔴"
                if col_mwr == "green":
                    emo1 = "🟢"
                else:
                    emo1 = "🔴"                    
                new_el = "    End Date: "    
                a = locale.currency(a, symbol=True, grouping=True)
                y = locale.currency(y, symbol=True, grouping=True)
                l = locale.currency(l, symbol=True, grouping=True)
                z = locale.currency(z, symbol=True, grouping=True)
                new_val = locale.currency(new_val, symbol=True, grouping=True)
                text1 = f":{col_change}[{x}]"
                text2 = f"📅:{col_change}[Inception Date:] :{col_change}[{b}]"
                text3 = f"🛑:{col_change}[{new_el}] :{col_change}[{c}]"
                text4 = f"💰:{col_change}[Invested Amount:] :{col_change}[{y.replace('.00','')}]"
                text5 = f"💰:{col_dep}[{store_val}:] :{col_dep}[{z.replace('.00','')}]"
                text6 = f"💰:{col_change}[Ending Value:] :{col_change}[{new_val.replace('.00', '')}]"
                text7 = f"💰:{col_change}[PnL:] :{col_change}[{a.replace('.00', '')}]"
                text8 = f"{emo} :{col_twr}[TWR:] :{col_twr}[{d:.2f}%]"
                text9 = f"{emo1} :{col_mwr}[MWR:] :{col_mwr}[{e*100:.2f}%]"
                
                locals()[f'{x}_button'] = st.sidebar.button(r'''{0}\
                                                            {1}\
                                                            {2}\
                                                            {3}\
                                                            {4}\
                                                            {5}\
                                                            {6}\
                                                            {7}\
                                                            {8}
                                                            '''.format(text1, text2, text3, text4, text5,
                                                                       text6, text7, text8, text9), 
                                                            use_container_width=False)
                if st.session_state.get(f'{x}') != True:
                    st.session_state[f'{x}'] = locals()[f'{x}_button']
                    
            index_of_4 = next((i for i in self.baskets if st.session_state[f"{i}"] == True), None) 
            print("index", index_of_4)           
            if st.session_state['button']==True:    
                for x in self.baskets:
                    st.session_state[f'{x}'] = False
                st.session_state['button'] = False
                self.fund_mwr_page(change_data, mn_wt, self.baskets)
            elif index_of_4 != None:
                func(self.baskets, self.init_cap, self.dp, self.end, self.change,
                self.start, self.end_date, self.twr, self.mwr, cap_data, 
                change_data, deposit_data, mtm_data, mtm_data_forex,
                pl, pl1, pl2, pl3, pl_col, pl_col1, pl_col2, pl_col3,
                head)  
            else:
                self.fund_mwr_page(change_data, mn_wt, self.baskets)
                     
        elif baskets_radio == 'Active Baskets':
            self.baskets = self.active_baskets
            self.init_cap = self.start_cap_active
            self.dp = self.dep_sum_active
            self.end = self.end_cap_active
            self.change = self.ch_sum_active
            self.start = self.start_date_active
            self.end_date = self.end_date_active
            self.twr = self.result_twr_active
            self.mwr = self.mwr_active_lst
            cap_data = self.cap_data
            change_data = self.ch
            deposit_data = self.dep
            mtm_data = self.mtm_data
            mtm_data_forex = self.mtm_data_forex
            pl = self.placeholder_basket
            pl1 = self.placeholder_basket1
            pl2 = self.placeholder_basket2
            pl3 = self.placeholder_basket3
            pl_col = self.st_col
            pl_col1 = self.en_col
            pl_col2 = self.view_col
            pl_col3 = self.view1_col
            head = self.sh
            mn_wt = self.mwr_active_lst
            
            for x, y, z, l, a, b, c, d, e in list(zip(self.baskets, self.init_cap, 
                                                self.dp, self.end, self.change,
                                                self.start, self.end_date,
                                                self.twr, self.mwr)):
                print('init for loop for active baskets')
                locale.setlocale(locale.LC_ALL, 'en_US')
                locale.override_localeconv = {'n_sign_posn':1}
                new_val = l+a
                a = locale.currency(a, symbol=True, grouping=True)
                y = locale.currency(y, symbol=True, grouping=True)
                l = locale.currency(l, symbol=True, grouping=True)
                col_dep = color_code(z,0) # deposits
                z = locale.currency(z, symbol=True, grouping=True)
                new_val = locale.currency(new_val, symbol=True, grouping=True)
                if col_dep == "red":
                    store_val = "Withdrawals"
                else:
                    store_val = "Deposits"                
                locals()[f'{x}_button'] = st.sidebar.button(f'''{x} 
                                                            
                                                           \n    Inception Date: {b}    End Date: {c}
                                                           \n    Invested Amount: {y.replace('.00','')}   {store_val}: {z.replace('.00','')}
                                                           \n    Ending Value: {new_val.replace('.00', '')}    PnL: {a.replace('.00', '')}
                                                           \n    TWR: {d:.2f}%        MWR: {e*100:.2f}%
                                                            ''', use_container_width=False)
                if st.session_state.get(f'{x}') != True:
                    st.session_state[f'{x}'] = locals()[f'{x}_button']            
            index_of_4 = next((i for i in self.baskets if st.session_state[f"{i}"] == True), None) 
            print("index", index_of_4)           
            if st.session_state['button']==True:    
                for x in self.baskets:
                    st.session_state[f'{x}'] = False
                st.session_state['button'] = False
                self.fund_mwr_page(change_data, mn_wt, self.baskets)
            elif index_of_4 != None:
                func(self.baskets, self.init_cap, self.dp, self.end, self.change,
                self.start, self.end_date, self.twr, self.mwr, cap_data, 
                change_data, deposit_data, mtm_data, mtm_data_forex,
                pl, pl1, pl2, pl3, pl_col, pl_col1, pl_col2, pl_col3,
                head)  
            else:
                self.fund_mwr_page(change_data, mn_wt, self.baskets)       
                #        locals()[f'{x}_button'] = st.button(f'{x}   {y}')
        #        if st.session_state.get(f'{x}') != True:
        #            st.session_state[f'{x}'] = locals()[f'{x}_button']
                            

            
            
spreadsheet_name1 = st.secrets["database"]["spreadsheet_name"]
spreadsheet_name = ast.literal_eval(spreadsheet_name1)
sheet = spreadsheet_name[5]
obj = basket_analysis(spreadsheet_name,sheet)
obj.main()
