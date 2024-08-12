import streamlit as st

major_col, major_col1 = st.columns([0.99, 0.01])
with st.expander('Metrics', expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('metric1', 1000000)
    with col2:
        st.metric('metric2', 1000000)
    with col3:
        st.metric('metric3', 100000000000)
        
