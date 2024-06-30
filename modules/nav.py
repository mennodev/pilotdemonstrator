import streamlit as st


def Navbar():
    with st.sidebar:
        st.page_link('streamlit_app.py', label='Welcome page', icon='🏡')
        st.page_link('pages/Betuwe.py', label='Betuwe', icon='📈')
        st.page_link('pages/NOP.py', label='NOP', icon='🌱')
        st.page_link('pages/Friese Wouden.py', label='Friese Wouden', icon='🌳')
        # add extra attention seeker to invite clicking on tabs
        st.sidebar.success("Select a tab above to choose the AOI")