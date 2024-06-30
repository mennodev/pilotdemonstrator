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

st.title("Pilot demonstrator showcase")

st.header("Welcome to the webapp landing page showcasing pilot demonstrator elements.")
st.write(
    """
    With the tabs in the sidebar different options to visualize the demonstrators in the AOIs are given.
    """
)




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

def style_function_betuwe(x):
    """
    Use color column to assign color
    """
    return {"color": 'darkgreen', "weight":2}

def style_function_nop(x):
    """
    Use color column to assign color
    """
    return {"color": 'darkgreen', "weight":2}

def style_function_fw(x):
    """
    Use color column to assign color
    """
    return {"color": 'darkgreen', "weight":2}

betuwe,nop,fw = load_AOIs_geojsons()

# Create a map with the GeoJSON data using folium
m = folium.Map(location=[sum(fw.total_bounds[[1, 3]]) / 2, sum(fw.total_bounds[[0, 2]]) / 2], zoom_start=8)


# Set the basemap URL
osm_tiles = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m)

# Add the Folium map to the Streamlit app using the st_folium library
#st_folium = st.container()
#with st_folium:
#    folium_static(m, width=900, height=600)
# add geojson and add some styling
folium.GeoJson(data=betuwe,
                        name = 'Betuwe',
                        style_function=style_function_betuwe,
                        tooltip = folium.GeoJsonTooltip(fields=['AOI'])
            ).add_to(m)

folium.GeoJson(data=nop,
                        name = 'Noord Oost Polder',
                        style_function=style_function_nop,
                        tooltip = folium.GeoJsonTooltip(fields=['AOI'])
            ).add_to(m)

folium.GeoJson(data=fw,
                        name = 'Friese wouden',
                        style_function=style_function_fw,
                        tooltip = folium.GeoJsonTooltip(fields=['AOI'])
            ).add_to(m)

map = st_folium(
    m,
    width=900, height=600,
    key="folium_map"
)