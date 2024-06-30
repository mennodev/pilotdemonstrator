import altair as alt
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import folium_static
import folium
from streamlit_folium import st_folium
from modules.nav import Navbar
# setup page config using modules
Navbar()

#    st.title(f'🔥 Individual Checker')

#st.set_page_config(page_title="Welcome",page_icon="🏡",)


st.title("Pilot demonstrator showcase")

st.header("Welcome to the webapp landing page showcasing pilot demonstrator elements.")
st.write(
    """
    With the tabs in the sidebar different options to visualize the demonstrators in the AOIs are given.
    """
)
# add extra attention seeker to invite clicking on tabs
st.sidebar.success("Select a tab above to choose the AOI")



# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data

def load_AOIs_geojsons():
    # Read GeoJSON data into a GeoDataFrame
    gdf1 = gpd.read_file("data/vectors/AOI_Betuwe.geojson")
    gdf2 = gpd.read_file("data/vectors/AOI_NOP.geojson")
    gdf3 = gpd.read_file("data/vectors/AOI_FrieseWouden.geojson")
    # concat
    
    # Convert the GeoDataFrame to a DataFrame
    #df = pd.DataFrame(gdf)
    return gdf1,gdf2,gdf3

def style_function(x):
    """
    Use color column to assign color
    """
    return {"color":x['properties']['color'], "weight":2}

betuwe,nop,fw = load_AOIs_geojsons()

# Create a map with the GeoJSON data using folium
m = folium.Map(location=[sum(nop.total_bounds[[1, 3]]) / 2, sum(nop.total_bounds[[0, 2]]) / 2], zoom_start=8)
# add geojson and add some styling
folium.GeoJson(data=gdf1,
                        name = 'Betuwe',
                        style_function={"color": 'green', "weight":2},
                        tooltip = folium.GeoJsonTooltip(fields=['AOI'])
            ).add_to(m)

folium.GeoJson(data=gdf2,
                        name = 'Noord Oost Polder',
                        style_function={"color": 'orange', "weight":2},
                        tooltip = folium.GeoJsonTooltip(fields=['AOI'])
            ).add_to(m)

folium.GeoJson(data=gdf3,
                        name = 'Friese wouden',
                        style_function={"color": 'dark green', "weight":2},
                        tooltip = folium.GeoJsonTooltip(fields=['AOI'])
            ).add_to(m)

# Set the basemap URL
osm_tiles = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m)
# Add the Folium map to the Streamlit app using the st_folium library
st_folium = st.container()
with st_folium:
    folium_static(m, width=900, height=600)
