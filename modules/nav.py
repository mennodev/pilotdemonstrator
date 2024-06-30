import streamlit as st


def Navbar():
    with st.sidebar:
        st.page_link('streamlit_app.py', label='Pilot Demonstrator', icon='🏡')
        st.page_link('pages/1_📈_Betuwe.py', label='Betuwe', icon='📈')
        st.page_link('pages/2_🌱_NOP.py', label='NOP', icon='🌱')
        st.page_link('pages/3_🌳_Friese Wouden.py', label='Friese Wouden', icon='🌳')
        # add extra attention seeker to invite clicking on tabs
        st.sidebar.success("Select a tab above to choose the AOI")