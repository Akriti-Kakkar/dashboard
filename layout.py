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
        
import streamlit as st

# HTML and CSS for side-by-side metrics
html_code = """
<div style="display: flex; justify-content: space-around;">
    <div style="text-align: center;">
        <h2>Metric 1</h2>
        <p>Value 1</p>
    </div>
    <div style="text-align: center;">
        <h2>Metric 2</h2>
        <p>Value 2</p>
    </div>
    <div style="text-align: center;">
        <h2>Metric 3</h2>
        <p>Value 3</p>
    </div>
</div>
"""

# Display the HTML in Streamlit
st.markdown(html_code, unsafe_allow_html=True)

        
