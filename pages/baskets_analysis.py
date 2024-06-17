import streamlit as st

class basket_analysis:
    def __init__(self, spreadsheet_name, database_name):
        
        '''
        spreadsheet sheets:
        1. change = done
        2. mtm (without forex) = done
        3. mtm with forex = done
        4. capital = done
        5. capital_eod = done
        6. cash flow_eod = done
        '''
        pass
    
    @staticmethod
    def page_config():
        st.set_page_config(page_title='Dashboard', page_icon='🌎', layout='wide')
        st.sidebar.image('htts_fund_logo.png', caption='HTTS Fund', )
        st.subheader('📈 Baskets Vs S&P Analysis')
        st.markdown('##')
    
    def baskets_mwr_page(self):
            pass
        
    def fund_mwr_page(self):
        pass
    
    def baskets_twr_page(self):
        pass
    
    def fund_twr_page(self):
        pass
    
    def template(self):
        pass
