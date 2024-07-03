import altair as alt
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import folium_static
import folium
from streamlit_folium import st_folium
from modules.nav import Navbar
import leafmap.foliumap as leafmap
from datetime import datetime


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

def load_cloudliness_data():
    df = pd.read_csv("data/dataframes/cloudliness_betuwe.csv",parse_dates=['datetime'])
    return df

def load_meteo_data():
    df = pd.read_csv("data/dataframes/debilt_cloudliness_meteo.txt",delimiter=',',parse_dates=['datetime'])
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


style = {
    "stroke": True,
    "color": "darkgreen",
    "weight": 2,
    "opacity": 1,
    "fill": True,
    "fillColor": "darkgreen",
    "fillOpacity": 0.1,
}

# Start of writing and plotting parts execute on screen
#load data
df_clouds = load_cloudliness_data()

st.subheader("Topic 1 : General succesfullnes of optical data reads")
st.write("""Most limiting factor for continuous and calibrated remote sensing with optical data is disturbance and occlusion due to atmospheric changes like clouds and cirrus. 
            To get an insight the general cloudliness in the AOI is explored.
            """)
# initialize slider
date_range_slider = st.slider(
    "Select a daterange to plot the Sentinel-2 cloudliness",
    min_value=datetime(2016, 1, 1),
    value= [datetime(2021, 1, 1),datetime(2024, 1, 1)],
    max_value=datetime(2024, 5, 31),
    )
st.write(f"Plotting AOI cloudliness for selecte date range **{date_range_slider[0]:%B %d, %Y}** and **{date_range_slider[1]:%B %d, %Y}**")
df_selection = df_clouds.loc[(df_clouds['datetime'] >= date_range_slider[0]) & (df_clouds['datetime'] <= date_range_slider[1])]
total_reads = len(df_selection.index)
df_unclouded = df_selection.loc[(df_selection['cloudliness'] <= 0.2)]
unclouded_reads = len(df_unclouded)
percentage = round((unclouded_reads/total_reads)*100,2)
# Display line chart
chart = alt.Chart(df_selection).mark_line().encode(
                x=alt.X('datetime:T', title='Date'),
                y=alt.Y('cloudliness:Q', title='Cloudliness'),
                #color='genre:N'
                ).properties(height=320)

st.altair_chart(chart, use_container_width=True)
st.write(f"""Found **{total_reads}** total Sentinel-2 reads!
    With **{unclouded_reads}** unclouded results yielding about **{percentage} %** usable imagery!            
        """)
st.write(f"""Check whether the cloudliness is spatially distributed within the AOI.
In order to check the spatial distribution in the AOI the following method is applied.
Use the cloud identification per pixel per read in the years ranging from 2016 to 2024 and calculate the percentage of unclouded pixels"""
)

m1 = folium.Map()
betuwe = gpd.read_file("data/vectors/AOI_Betuwe.geojson")
#m1.add_geojson('data/vectors/AOI_Betuwe.geojson', layer_name="Betuwe", style=style)
#raster_path = 'data/rasters/2022-12-23_clipped.tif'
image_cloudliness = 'data/rasters/cloudliness_betuwe_colored.png'
#image_bounds = [[-20.664910, -46.538223], [-20.660001, -46.532977]]
image_bounds_parcels = [[51.9240070190000012,5.3419835630000003],[51.9703482809999997,5.4335150150000002]]
image_bounds_betuwe = [[51.8516565146628992,5.2416696828374079],[51.9855054919967117,5.8974398402446582]]
# 
folium.raster_layers.ImageOverlay(
    image=image_cloudliness,
    name="image overlay",
    opacity=1,
    bounds=image_bounds_betuwe,
).add_to(m1)
m1.fit_bounds(image_bounds_betuwe, padding=(0, 0))
# add layer control
#folium.LayerControl(collapsed=False).add_to(m1)
control = folium.LayerControl(collapsed=False)
map = st_folium(
    m1,
    width=900, height=500,
    key="folium_map",
    layer_control=control
)
url_knmi = 'https://www.knmi.nl/home'
st.write(f"The cloud free pixel range between 35-40 so very low variability in the AOI, but there is some spatial distribution")
st.write(f"Check whether the reads are in line with meteorological reads by the [KNMI]({url_knmi})")
df_debilt = load_meteo_data()
date_range_slider_meteo = st.slider(
    "Select a daterange to plot the Sentinel-2 cloudliness",
    min_value=datetime(2016, 1, 1),
    value= [datetime(2021, 1, 1),datetime(2024, 1, 1)],
    max_value=datetime(2024, 6, 2),
    )
st.write(f"""Plotting cloudliness according to meteo for selecte date range **{date_range_slider_meteo[0]:%B %d, %Y}** and **{date_range_slider_meteo[1]:%B %d, %Y}**.
0 indicate unclouded coditions to  9 indicating total cloudcover""")
df_selection_meteo = df_debilt.loc[(df_debilt['datetime'] >= date_range_slider_meteo[0]) & (df_debilt['datetime'] <= date_range_slider_meteo[1])]
total_reads_meteo = len(df_selection_meteo.index)
df_unclouded_meteo = df_selection_meteo.loc[(df_selection_meteo['cloudscale'] <= 1)]
unclouded_reads_meteo = len(df_unclouded_meteo.index)
percentage_meteo = round((unclouded_reads_meteo/total_reads_meteo)*100,2)
# Display line chart
chart_meteo = alt.Chart(df_selection_meteo).mark_line().encode(
                x=alt.X('datetime:T', title='DateTime'),
                y=alt.Y('cloudscale', title='Cloudlines (0-9)'),
                #color='genre:N'
                ).properties(height=320)

st.altair_chart(chart_meteo, use_container_width=True)
st.write(f"""Found **{total_reads_meteo}** total meteo reads!
    With **{unclouded_reads_meteo}** unclouded results meaning that overall about **{percentage_meteo} %** skies are unclouded!            
        """)
container = st.container(border=True)
container.write(f"**Conclusion**")
container.write(f"""
                High occurence and variability of clouds in the AOI leading to drastic reduction of succesfull reads with optical imagery.
                Introducing higher cadence mitigates many issues of unsuccesfull reads, but some extended intervals (multiple weeks) with cloud occurence remain in the AOI
                """)

#try:
#    m1.add_raster(raster_path, indexes=[4,3,2],layer_name='Planet')
#except ImportError as e:
#    st.write(f"Something went wrong {e}")
#m1.to_streamlit(height=600)

map = st_folium(
    m1,
    width=900, height=500,
    key="folium_map"
)

# Add the Folium map to the Streamlit app using the st_folium library
url_cbs = 'https://www.cbs.nl/nl-nl/cijfers/detail/7140gras'
st.subheader("Topic 2 : Grassland management in the Betuwe")
st.write(f"""Grass is a major **fodder** crop in the Netherlands and is utilized via **grazing** by livestock and **mowing**. 
            The [central bureau for statistics (CBS)]({url_cbs}) published data on grasslandmowing presented in the table below.
            Using this data we can estimate that traditionally on average a grass field is mowed between 2.1 to 2.85 times.
            However some fields will not be mowed at all due to grazing, so the numbers of 'cuts' per season will be much higher for other grassland parcels.
            The first cut of the season is much dependant on weather conditions. The temperature sum (TSum) is a good proxy to determine grassland readiness.
            In the fall and winter, after Octobre traditionally no mowing is performed as well due to the risk of frost damage.
            Below we will further explore the grasslands, the management and CAP related regulation in the AOI 'Betuwe'.
            """)
cbs_df = pd.read_csv("data/dataframes/Grassland_statistics.csv",delimiter=';',dtype=str)
st.table(cbs_df)

# When the user interacts with the map
# Create a map with the GeoJSON data using folium
st.write(f"""LPIS data for the AOI reveals the following
""")


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
