import streamlit as st


def Navbar():
    with st.sidebar:
        st.page_link('streamlit_app.py', label='Pilot Deomonstrator', icon='🏡')
        st.page_link('pages/1_📈_Betuwe.py', label='Betuwe', icon='📈')
        st.page_link('pages/2_🌱_NOP.py', label='NOP', icon='🌱')
        st.page_link('pages/3_🌳_Friese Wouden.py', label='Friese Wouden', icon='🌳')