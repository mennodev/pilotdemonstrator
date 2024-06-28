import altair as alt
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import folium_static
import folium

# Show the page title and description.
st.set_page_config(page_title="Betuwe grasslands analysis", page_icon="📈")
st.title("📈 Analysis of cadency for grassland monitoring for the CAP")
st.write(
    """
    This app visualizes data to illustrate the means to monitor grasslands in the CAP as a pilot demonstrator!
    """
)


# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/dataframes/NDVI_GrasslandsParcels_Betuwe2023_pq.csv")
    return df

def load_parquet():
    df = pd.read_parquet("data/dataframes/NDVI_GrasslandsParcels_Betuwe2023_pq.parquet", engine='pyarrow')
    return df

def load_geojson():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/LPIS_Grasslands.geojson")
    # Convert the GeoDataFrame to a DataFrame
    df = pd.DataFrame(gdf)
    return df

def style_function(x):
    return {"color":"blue", "weight":3}


df = load_parquet()
vector = load_geojson()

# Create a map with the GeoJSON data using folium
m = folium.Map(location=[sum(gdf.total_bounds[[1, 3]]) / 2, sum(gdf.total_bounds[[0, 2]]) / 2], zoom_start=12)
# add geojson and add some styling
folium.GeoJson(data=gdf,
                        name = 'Grass fields',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','gws_gewas','gewascode'])
            ).add_to(m)

# Set the basemap URL
osm_tiles = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m)
# Add the Folium map to the Streamlit app using the st_folium library
st_folium = st.container()
with st_folium:
    folium_static(m, width=700, height=500)

# Display the data as a table using `st.dataframe`.
st.dataframe(
    df,
    use_container_width=True,
    column_config={"gid": st.column_config.TextColumn("gid")},
)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df.reset_index()
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("date:N", title="Date"),
        y=alt.Y("NDVI:Q", title="NDVI"),
        color="gid:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
