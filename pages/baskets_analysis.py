import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from stats import *
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read()

# Print results.
#for row in df.itertuples():
#    st.write(f"{row.WeekNum}:")

df = conn.read(
    worksheet="capital"
)
st.write(df.tail(30))

class basket_analysis:
    def __init__(self, spreadsheet_name: list, database_name: str) -> None:
        
        '''
        spreadsheet sheets:
        1. change = done
        2. mtm (without forex) = done
        3. mtm with forex = done
        4. capital = done
        5. capital_eod = done
        6. cash flow_eod = done
        '''
        self.spreadsheet_name = spreadsheet_name
        self.database_name = database_name
    
    @staticmethod
    def page_config() -> None:
        st.set_page_config(page_title='Dashboard', page_icon='🌎', layout='wide')
        st.sidebar.image('htts_fund_logo.png', caption='HTTS Fund')
        st.subheader('📈 Baskets Vs S&P Analysis')
        # Inject custom CSS to set the width of the sidebar
        st.markdown("""
            <style> section[data-testid="stSidebar"] { width: 505px !important; }
            </style>
        """, unsafe_allow_html=True)
        
    def get_data(self):
        capital_data = pd.read_excel(self.database_name, 
                                     sheet_name=self.spreadsheet_name[0])
        capital_data = capital_data.set_index('Date')
        st.write(capital_data)
        baskets_lst = capital_data.columns.tolist()
        baskets_lst = baskets_lst[2:]
        st.write(baskets_lst)
        active_baskets = [col for col in capital_data.columns if 
                          capital_data[col].isna().iloc[-1]!=True]
        active_baskets = active_baskets[2:]
        cashflow_data = pd.read_excel(self.database_name, 
                                sheet_name=self.spreadsheet_name[4])
        cashflow_data = cashflow_data.set_index('Date')
        change_data = pd.read_excel(self.database_name, 
                                    sheet_name=self.spreadsheet_name[1])
        change_data = change_data.set_index('Date')
        self.change_data = change_data
        self.cashflow_data = cashflow_data
        self.capital_data = capital_data
        self.baskets_lst = baskets_lst
        self.active_baskets = active_baskets
    
    def baskets_mwr_page(self):
            pass
        
    def fund_mwr_page(self):
        pass
    
    def baskets_twr_page(self):
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
        st.write(self.change_data)
        st.write(ch)
        result_twr  = daily_twr_data.apply(lambda col: last_n_twr(
            daily_twr_data, col.name, len(daily_twr_data.dropna(subset=col.name)), True
        )) * 100
        result_twr_active  = daily_twr_active_data.apply(lambda col: last_n_twr(
            daily_twr_active_data, col.name, len(daily_twr_active_data.dropna(subset=col.name)), True
        )) * 100        
        result_wt_cash = last_n_weighted_cash_flow(ch['Intra Decorrelation'],
                                                   dep['Intra Decorrelation'],
                                                   cap_data['Intra Decorrelation'])
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
        st.write(mwr_lst)
        
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
        st.write(mwr_active_lst)
        
        result_wt_cash1 = last_n_weighted_cash_flow(ch['Global Intra Cor'],
                                                   dep['Global Intra Cor'],
                                                   cap_data['Global Intra Cor'])
        st.write('MWR')
        st.write(last_n_mwr(result_wt_cash[0], ch['Intra Decorrelation'], result_wt_cash[1])*100)
        st.write(last_n_mwr(result_wt_cash1[0], ch['Global Intra Cor'], result_wt_cash1[1])*100)
        st.write('wt cash')
        st.write(result_wt_cash1)
        st.write(dep)
        st.write(ch['Global Intra Cor'].sum())
    
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
        
    def fund_twr_page(self):
        pass
    
    def template(self):
        pass

    def main(self):
        self.page_config()
        self.get_data()
        self.baskets_twr_page()
        baskets_radio = st.sidebar.radio('Baskets Selection' ,
                                         options=['Active Baskets', 'Baskets 2024'], horizontal=True)
        button1 = st.sidebar.button('Exit View')
        if st.session_state.get('button') != True:
            st.session_state['button'] = button1
                
        
        def func(basket, cap, deposit, endcap, change, start, end_date, twr,
                 mwr): 
            for x, y, z, l, a, b, c, d, e in list(zip(basket, cap, deposit, endcap, change, start, end_date,
                                                twr, mwr)):   
                if st.session_state[f'{x}'] == True:
                    lst1 = [w for w in basket]
                    lst1.remove(x)
                    print(basket)
                    print(cap)
                    if any((st.session_state[f'{key}'] == True) for key in lst1):
                        st.write('''Click on 'Exit View' before switching between buttons.''')
                        break
                    else:
                        st.write(f'Content for {x} is upcoming')
                        locals()[f'{x}_stats'] = st.radio('Stats', ('MWR', 'TWR'), key=f'{x,y}')
                        if locals()[f'{x}_stats'] == 'MWR':
                            st.markdown('testtesttesttesttesttesttesttest')
                            st.info('Info')
                            st.metric('info', 700)
                            data = pd.DataFrame({'col': [x for x in range(100)], 'col2': [x for x in range(101,201)]})
                            plt.hist(x='col')
                            st.pyplot()
                        elif locals()[f'{x}_stats'] == 'TWR':
                            data = pd.DataFrame({'col': [x for x in range(100)], 'col2': [x for x in range(101,201)]})
                            st.write(data)        
                
        if baskets_radio == 'Baskets 2024':
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
            
            for x, y, z, l, a, b, c, d, e in list(zip(self.baskets, self.init_cap,
                                                self.dp, self.end, self.change, 
                                                self.start, self.end_date,
                                                self.twr, self.mwr)):
                print('init for loop for baskets 2024')
                locals()[f'{x}_button'] = st.sidebar.button(f'''{x} 
                                                            
                                                           \n    Inception Date: {b}    End Date: {c}
                                                           \n    Invested Amount: {int(y)}   Deposits: {int(z)}
                                                           \n    Ending Value: {int(l+a)}      Change: {a}
                                                           \n    TWR: {d}        MWR: {e}
                                                            ''', use_container_width=False)
                if st.session_state.get(f'{x}') != True:
                    st.session_state[f'{x}'] = locals()[f'{x}_button']
            
            if st.session_state['button']:    
                for x in self.baskets:
                    st.session_state[f'{x}'] = False
                st.session_state['button'] = False
            else:
                func(self.baskets, self.init_cap, self.dp, self.end, self.change,
                     self.start, self.end_date, self.twr, self.mwr)
                     
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
            
            for x, y, z, l, a, b, c, d, e in list(zip(self.baskets, self.init_cap, 
                                                self.dp, self.end, self.change,
                                                self.start, self.end_date,
                                                self.twr, self.mwr)):
                print('init for loop for active baskets')
                locals()[f'{x}_button'] = st.sidebar.button(f'''{x} 
                                                            
                                                           \n    Inception Date: {b}    End Date: {c}
                                                           \n    Invested Amount: {int(y)}   Deposits: {int(z)}
                                                           \n    Ending Value: {int(l+a)}      Change: {a}
                                                           \n    TWR: {d}        MWR: {e}
                                                            ''', use_container_width=False)
                if st.session_state.get(f'{x}') != True:
                    st.session_state[f'{x}'] = locals()[f'{x}_button']            
            if st.session_state['button']:    
                for x in self.baskets:
                    st.session_state[f'{x}'] = False
                st.session_state['button'] = False
            else:
                print('else in active baskets, self.baskets', self.baskets)
                func(self.baskets, self.init_cap, self.dp, self.end, self.change,
                     self.start, self.end_date, self.twr, self.mwr)            
                #        locals()[f'{x}_button'] = st.button(f'{x}   {y}')
        #        if st.session_state.get(f'{x}') != True:
        #            st.session_state[f'{x}'] = locals()[f'{x}_button']
                            

            
            
spreadsheet_name = ['capital', 'change', 'mtm', 'mtm_forex', 'cash_flows']
database_name = 'dashboard_2024.xlsx'
obj = basket_analysis(spreadsheet_name, database_name)
obj.main()
