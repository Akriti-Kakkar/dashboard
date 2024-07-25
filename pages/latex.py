from termcolor import colored, cprint

import streamlit as st

import sys

text = colored("Latex Format", "green")
text1 = colored("new stuff", "red")

st.latex(text)

st.write(text)

st.html(text)

st.markdown(text)

st.write(f"${{text}}$", f"${{text1}}$")

st.button(f''':red[${{text}}$]
          
          :blue[${{text1}}$]''')

st.write(r"${}$".format(text))

st.write(r"""{}
         
         {}""".format(text, text1))
txt = """{}
         
         {}""".format(text, text1)

st.code(text, language="python")

st.text(text)

st.write('''
         :red[streamlit] :orange[can]
         :gray[pretty]
         ''')

st.markdown('''
            :red[streamlit] :orange[can]
            :gray[pretty]
            ''')

st.button(''':red[streamlit]\n Basket: :orange[can]\n: Inception: gray[pretty]\nTWR: :rainbow[-10%]''')

text1='streamlit'
text2='$100,000'
text3='-10%'
text4='2024-09-01'
st.button(f''':red[{text1}]\n Basket: :orange[{text2}]\n: Inception: :gray[{text3}]\nTWR: :rainbow[{text4}]''')

c = 'red'
c1 = 'green'
c2 = " "
c3 = '\t \t'
c4 = "  net"
st.button(f''':{c}[{text1}] \
    \n:red[Basket:] :{c}[{text2}]\n \nInception: :{c1}[{text3}]\n\nTWR: :{c1}[{text4}]''')

st.button(f''':blue[x\t]\n \
     \t \n{c2} ✅:blue[new:] {c2} :blue[new1] \b {c2} 🛑:blue[{c4:}] {c2} :blue[1000000]''', 
          use_container_width=True)
st.metric(":green[Metric]",  200000)
#st.status('Success')
#finalized
text = ":green[$$Latex Format$$]"
text1 = ":gray[$$new stuff$$]"
st.button(r"${} \\textcolor{{red}}{{{}}}$".format(text, text1), use_container_width=True)
st.button(r"{}$\>$ $\>$ $\>$ $\>${}".format(text, text1), use_container_width=True)
