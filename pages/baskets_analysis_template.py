import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly
lst = ['basket1', 'basket2', 'basket3']
change = [100, 200, 1000]
'''
for x, y in list(zip(lst, change)):
    with st.popover(f'{x}, {y}'):
        try:
            st.write(f'Content for {x} is upcoming')
            stats1 = st.radio('Stats', ('MWR', 'TWR'))
            if stats1 == 'MWR':
                st.markdown('testtesttesttesttesttesttesttest')
                st.info('Info')
                st.metric('info', 700)
                data = pd.DataFrame({'col': [x for x in range(100)], 'col2': [x for x in range(101,201)]})
                plt.hist(x='col')
                st.pyplot()
            elif stats1 == 'TWR':
                st.write(data)
            # plt.savefig('plt.png')
        except:
            pass
'''
'''
Final blue print: keep active baskets in sidebar. 
1. default page is htts with 2 options all baskets and htts fund
(applying same metrics method asall the baskets)
2. create methods and add only the methods in the loop
3. Effort required: create mwr and twr views for one set (and iterate it over all baskets and default fund)
'''

button1 = st.button('Exit View')
if st.session_state.get('button') != True:
    st.session_state['button'] = button1
    
for x, y in list(zip(lst, change)):
    locals()[f'{x}_button'] = st.button(f'{x}   {y}')
    if st.session_state.get(f'{x}') != True:
        st.session_state[f'{x}'] = locals()[f'{x}_button']
    
if st.session_state['button']:    
    for x in lst:
        st.session_state[f'{x}'] = False
    st.session_state['button'] = False
    
else:    
    for x, y in list(zip(lst, change)):
#        locals()[f'{x}_button'] = st.button(f'{x}   {y}')
#        if st.session_state.get(f'{x}') != True:
#            st.session_state[f'{x}'] = locals()[f'{x}_button']
            
        if st.session_state[f'{x}'] == True:
            lst1 = [w for w in lst]
            lst1.remove(x)
            print(lst)
            print(lst1)
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
        
        
import streamlit as st
from streamlit_modal import Modal
import pandas as pd
import matplotlib.pyplot as plt
modal = Modal(key="Demo Key",title="test")
col1, col2 = st.columns(2)
columns = [col1, col2]
for col in columns:
    with col:
        open_modal = st.button(label='button{}'.format(col))
        if open_modal:
            with modal.container():
                st.markdown('testtesttesttesttesttesttesttest')
                st.info('Info')
                st.metric('info', 700)
                data = pd.DataFrame({'col': [x for x in range(100)]})
                data.plot()
                plt.show()