import streamlit as st

st.set_page_config(page_title='Dashboard', page_icon='🌎', layout="wide",
                           initial_sidebar_state="expanded")

st.header("Design 1: collapsable metric window for each row, highlighting features of the metric in its name ")
major_col, major_col1 = st.columns([0.99, 0.01])
with st.expander('Winning Stats For The Year 2022', expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('metric1', 1000000)
    with col2:
        st.metric('metric2', 1000000)
    with col3:
        st.metric('metric3', 10000000000)
        
st.header("Design 2: simple side by side html view of metrics in mobile and laptop view")
# HTML and CSS for side-by-side metrics
html_code = f"""
<div style="display: flex; justify-content: space-around;">
    <div style="text-align: center;">
        <h2>Metric 1</h2>
        <p>1000000</p>
        <h2>Metric 4</h2>
        <p>40%</p>        
    </div>
    <div style="text-align: center;">
        <h2>Metric 2</h2>
        <p>1000000</p>
        <h2>Metric 5</h2>
        <p>1000%</p>        
    </div>
    <div style="text-align: center;">
        <h2>Metric 3</h2>
        <p>100000000000</p>
        <h2>Metric 6</h2>
        <p>60 Days</p>        
    </div>
</div>
"""

# Display the HTML in Streamlit
st.markdown(html_code, unsafe_allow_html=True)

        

#<div style="display: flex; justify-content: space-around;">
#    <div style="text-align: center;">
#        <h1>Metric 1</h1>
#        <h2>1000000</h2>
#        <h3>s&p: 70000000000</h3>
#        <p>"Basket underperformed s&p"</p>
#        <h2>Metric 4</h2>
#        <p>40%</p>        
#    </div>
