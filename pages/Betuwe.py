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
# setup page config
#st.set_page_config(page_title="Welcome",page_icon="🏡",)


st.title("Pilot demonstrator AOI Betuwe")

st.header("Demonstrator focusing on grassland management in the CAP and relation to cadency")
st.write(
    """
    Below you find different blocks of data visualization developed in the pilot demonstrator exploring different topics. 
    """
)

# Helper functions

# Translation dictionary
translation_dict = {
    'Grasland, blijvend': 'Grassland, permanent',
    'Grasland, natuurlijk. Met landbouwactiviteiten.': 'Natural grassland with agricultural activities',
    'Agrarisch natuurmengsel': 'Mixed nature and agricultural seeds',
    'Grasland, tijdelijk': 'Grassland, temporary'
}
# Color dictionary
color_dict = {
    'Grasland, blijvend': 'green',
    'Grasland, natuurlijk. Met landbouwactiviteiten.': 'darkgreen',
    'Agrarisch natuurmengsel': 'yellow',
    'Grasland, tijdelijk': 'orange'
}
def get_pos(lat, lng):
    return lat, lng

def get_gid_from_tooltip(tooltip_info):
    """
    very hacky but could not find any normal way to get only gid from tooltip
    """
    splitter = str(tooltip_info).split('gid')
    gid = int(splitter[1].split("management")[0])
    return gid
# Show the page title and description.
#st.set_page_config(page_title="Betuwe grasslands analysis", page_icon="📈")



# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/dataframes/NDVI_GrasslandsParcels_Betuwe2023_pq.csv")
    return df

def load_meteo_data():
    df = pd.read_csv("data/dataframes/debilt_cloudliness_meteo.txt",delimiter=',')
    return df

def load_parquet():
    df = pd.read_parquet("data/dataframes/NDVI_GrasslandsParcels_Betuwe2023_pq.parquet", engine='pyarrow')
    return df

def load_geojson():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/LPIS_Grasslands.geojson")
    # translate to English
    gdf['management'] = gdf['gws_gewas'].map(translation_dict)
    gdf['color'] = gdf['gws_gewas'].map(color_dict)
    # Convert the GeoDataFrame to a DataFrame
    #df = pd.DataFrame(gdf)
    return gdf

def style_function(x):
    """
    Use color column to assign color
    """
    return {"color":x['properties']['color'], "weight":2}

def style_function_betuwe(x):
    """
    Use color column to assign color
    """
    return {"color":'darkgreen', 'fillOpacity': .1 , "weight":2}


# Start of writing and plotting parts execute on screen

st.subheader("Topic 1 : General optical data availability")
st.write("Explore general cloudliness in the AOI")
betuwe = gpd.read_file("data/vectors/AOI_Betuwe.geojson")


# Create a map with the GeoJSON data using folium
m1 = folium.Map(location=[sum(betuwe.total_bounds[[1, 3]]) / 2, sum(betuwe.total_bounds[[0, 2]]) / 2], zoom_start=11)
# add geojson and add some styling
folium.GeoJson(data=betuwe,
                        name = 'Betuwe',
                        style_function=style_function_betuwe,
                        ).add_to(m1)
# add raster to the map
image_bounds = [[51.8516565150000019,5.2416696829999996], [51.9855054920000015,5.8974398399999997]]
folium.raster_layers.ImageOverlay(
    image='data/rasters/cloudliness_betuwe1.png',
    name="Cloudliness heatmap",
    opacity=1,
    bounds=image_bounds,
).add_to(m1)

# Set the basemap URL
osm_tiles = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m1)
map = st_folium(
    m1,
    width=900, height=600,
    key="folium_map"
)

# Add the Folium map to the Streamlit app using the st_folium library
st.subheader("Topic 2 : Sentinel-2 availability for Grassland management markers")
st.write("Explore availability of Sentinel-2 for subset grassland parcels in the AOI")
# When the user interacts with the map
# Create a map with the GeoJSON data using folium

geojson = load_geojson()

m = folium.Map(location=[sum(geojson.total_bounds[[1, 3]]) / 2, sum(geojson.total_bounds[[0, 2]]) / 2], zoom_start=11)
# add geojson and add some styling
folium.GeoJson(data=geojson,
                        name = 'Betuwe',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)


# Set the basemap URL
osm_tiles = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m)
map = st_folium(
    m,
    width=900, height=600,
    key="folium_map"
)

df = load_parquet()

gid_to_plot = 71757
if map.get("last_object_clicked_tooltip"):
    gid_to_plot = get_gid_from_tooltip(map["last_object_clicked_tooltip"])
if gid_to_plot is not None:
    # subselect data
    df_selection = df.loc[df['gid'] == gid_to_plot]
    #st.dataframe(data=df_selection.head(20))
    # Display line chart
    chart = alt.Chart(df_selection).mark_line().encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('NDVI:Q', title='NDVI'),
                #color='genre:N'
                ).properties(height=320)
    st.write('Chart of succesfull NDVI reads by Sentinel-2')
    st.altair_chart(chart, use_container_width=True)
