import streamlit as st
from modules.nav import Navbar
# setup page config using modules
Navbar()

st.title("NOP")

st.header("Pilot demonstrator for the NOP")
st.write(
    """With the tabs in the sidebar different options to visualize the grassland monitor are given.
    One option is to graph the NDVI over time of the grassland plots. The second option is to plot the NDVI on a map per date.
    """
)