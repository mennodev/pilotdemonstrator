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
from shapely import wkt

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
    'Grasland, tijdelijk': 'Grassland, temporary',
    'Groene braak, spontane opkomst': 'Fallow (green manuring), unmanaged',
    "Peren. Aangeplant voorafgaande aan lopende seizoen.": 'Pear trees',
    "Appels. Aangeplant voorafgaande aan lopende seizoen.": 'Apple trees',
    "Appels. Aangeplant lopende seizoen.":'Apple trees, newly planted',
    "Peren. Aangeplant lopende seizoen.":'Pear trees, newly planted',
    "Engels raaigras, groenbemesting, vanggewas":'Perrenial ryegrass (green manuring)',
    "Tagetes patula (Afrikaantje)": "Tagetes patula (marigold)",
    "Italiaans raaigras, groenbemesting, vanggewas": 'Italian ryegrass (green manuring)',

}
# Color dictionary
color_dict = {
    'Grasland, blijvend': 'green',
    'Grasland, natuurlijk. Met landbouwactiviteiten.': 'darkgreen',
    'Agrarisch natuurmengsel': 'yellow',
    'Grasland, tijdelijk': 'orange',
    'Groene braak, spontane opkomst': 'lightgreen',
    "Peren. Aangeplant voorafgaande aan lopende seizoen.": 'khaki',
    "Appels. Aangeplant voorafgaande aan lopende seizoen.": 'red',
    "Appels. Aangeplant lopende seizoen.":'red',
    "Peren. Aangeplant lopende seizoen.":'khaki',
    "Engels raaigras, groenbemesting, vanggewas":'lightgreen',
    "Tagetes patula (Afrikaantje)": 'lightgreen',
    "Italiaans raaigras, groenbemesting, vanggewas": 'lightgreen',
}

# Color dictionary
color_dict_testfields = {
    4: 'darkgreen',
    3: 'green',
    2: 'yellow',
    1: 'orange',
    0: 'red'
}

# Define colors for the events
event_colors = {
    'Mowing': 'darkgreen',
    'Grazing': 'lightgreen'
}

# Define the mapping from orbit numbers to the desired string values
orbit_mapping = {
    161: 'A161',
    88: 'A088',
    37: 'D037',
    110: 'D110'
}

coh_mapping = {
    'cohvv': 'VV',
    'cohvh': 'VH'
}


def parse_dates(date_str):
    if pd.notnull(date_str) and date_str.startswith('20'):
        return [datetime.strptime(date, '%Y%m%d') for date in date_str.split('_')]
    return []

def get_pos(lat, lng):
    return lat, lng

def get_gid_from_tooltip(tooltip_info):
    """
    very hacky but could not find any normal way to get only gid from tooltip
    """
    splitter = str(tooltip_info).split('gid')
    gid = int(splitter[1].split("management")[0])
    return gid

def get_fid_from_tooltip(tooltip_info):
    """
    very hacky but could not find any normal way to get only gid from tooltip
    """
    splitter = str(tooltip_info).split('fid')
    fid = int(splitter[1].split("mowed")[0])
    return fid
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
    # add hourly info
    df['hour'] = df['datetime'].dt.hour
    return df

def load_meteo_data_daytime():
    df = pd.read_csv("data/dataframes/meteo_daytime.txt",delimiter=',',parse_dates=['datetime'])
    return df

def load_parquet():
    df = pd.read_parquet("data/dataframes/NDVI_GrasslandsParcels_Betuwe2023_pq.parquet", engine='pyarrow')
    return df

def load_GRD_parquet():
    df = pd.read_parquet("data/dataframes/GRD_GrasslandsParcels_Betuwe2023_pq.parquet", engine='pyarrow')
    # Apply the mapping to the 'orbit' column to change from numbers to string with Ascending and Descending
    df['orbit'] = df['orbit'].map(orbit_mapping)
    return df

def load_parquet_tf():
    df = pd.read_parquet("data/dataframes/NDVI_GrasslandsParcels_Betuwe2022_pq.parquet", engine='pyarrow')
    return df

def load_GRD_parquet_tf():
    df = pd.read_parquet("data/dataframes/GRD_GrasslandsParcels_Betuwe2022_pq.parquet", engine='pyarrow')
    # Apply the mapping to the 'orbit' column to change from numbers to string with Ascending and Descending
    df['orbit'] = df['orbit'].map(orbit_mapping)
    return df

def load_coh_csv():
    df = pd.read_csv("data/dataframes/coh_grassland_parcels_maurik.csv")
    return df

def load_conv_csv():
    df = pd.read_csv("data/dataframes/conv_grassland_parcels_maurik.csv")
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

def load_geojson_testfields():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/Fields_AOI_Betuwe_WGS84_grassland_maurik_brp_gid.geojson")
    # translate to English
    gdf['management'] = gdf['gws_gewas'].map(translation_dict)
    gdf['color'] = gdf['mowed'].map(color_dict_testfields)
    # Convert the GeoDataFrame to a DataFrame
    #df = pd.DataFrame(gdf)
    return gdf

def load_geojson_bufferstrips():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/Fields_AOI_Betuwe_WGS84_bufferstrips_fruit_brp_gid.geojson")
    # translate to English
    gdf['management'] = gdf['gws_gewas'].map(translation_dict)
    gdf['color'] = gdf['gws_gewas'].map(color_dict)
    # Convert the GeoDataFrame to a DataFrame
    #df = pd.DataFrame(gdf)
    return gdf


def load_planet_fusion_csv():
    df = pd.read_csv("data/dataframes/PlanetFusionNDVI.csv")
    # parse geometries for geopandas using shapely wkt
    df['geometry'] = df['geometry'].apply(wkt.loads)
    # make gdf with geopandas
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:32631")
    # Transform the GeoDataFrame to WGS84 (EPSG:4326)
    gdf = gdf.to_crs(epsg=4326)
    gdf['management'] = gdf['gws_gewas'].map(translation_dict)
    gdf['color'] = gdf['gws_gewas'].map(color_dict)
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

def style_function_bufferstrips(x):
    """
    Use color column to assign color
    """
    return {"color":x['properties']['color'], "weight":2, "fillOpacity":0.0}

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

st.subheader("Topic 1 : General succesfulness of optical data reads")
st.write("""Most limiting factor for continuous and calibrated remote sensing with optical data is disturbance and occlusion due to atmospheric changes like clouds and cirrus. 
            To get an insight the general cloudiness in the AOI is explored.
            """)
# initialize slider
date_range_slider = st.slider(
    "Select a daterange to plot the Sentinel-2 cloudiness",
    min_value=datetime(2016, 1, 1),
    value= [datetime(2022, 3, 1),datetime(2022, 9, 1)],
    max_value=datetime(2024, 5, 31),
    )
st.write(f"Plotting AOI cloudiness for the selected date range **{date_range_slider[0]:%B %d, %Y}** and **{date_range_slider[1]:%B %d, %Y}**")
df_selection = df_clouds.loc[(df_clouds['datetime'] >= date_range_slider[0]) & (df_clouds['datetime'] <= date_range_slider[1])]
total_reads = len(df_selection.index)
df_unclouded = df_selection.loc[(df_selection['cloudliness'] <= 0.2)]
unclouded_reads = len(df_unclouded)
percentage = round((unclouded_reads/total_reads)*100,2)
# Display line chart
chart = alt.Chart(df_selection).mark_bar().encode(
                x=alt.X('datetime:T', title='Date'),
                y=alt.Y('cloudliness:Q', title='Cloudiness'),
                #color='genre:N'
                ).properties(height=320)

st.altair_chart(chart.interactive(), use_container_width=True)
st.write(f"""Found **{total_reads}** total Sentinel-2 reads!
    With **{unclouded_reads}** unclouded results yielding about **{percentage} %** usable imagery!            
        """)
st.write(f"""Check whether the cloudiness is spatially distributed within the AOI.
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
    width=700, height=300,
    key="folium_map",
    layer_control=control
)
st.write(f"The cloud free pixel values are represented ranging from darkorange (35% cloud free) to green (40% cloud free). So it can be seen that the cloudiness variability in the AOI is very low, but there is some spatial distribution.")
url_knmi = 'https://www.knmi.nl/home'
st.write(f"Check whether the reads are in line with meteorological reads by the [KNMI]({url_knmi})")

df_debilt = load_meteo_data()
date_range_slider_meteo = st.slider(
    "Select a daterange to plot the meteorological cloudiness",
    min_value=datetime(2016, 1, 1),
    value= [datetime(2022, 1, 1),datetime(2023, 1, 1)],
    max_value=datetime(2024, 6, 2),
    )
date_range_slider_hours = st.slider(
    "Select an hour range to plot the meteorological cloudiness",
    min_value=1,
    value= [10,15],
    max_value=24,
    )
st.write(f"""Plotting cloudiness according to meteo between the hours **{date_range_slider_hours[0]}** and **{date_range_slider_hours[1]}** for the selected date range **{date_range_slider_meteo[0]:%B %d, %Y}** and **{date_range_slider_meteo[1]:%B %d, %Y}**.""")
st.write(f"""0 indicate unclouded conditions to 9 indicating total cloudcover""")

df_selection_meteo = df_debilt.loc[(df_debilt['datetime'] >= date_range_slider_meteo[0]) & (df_debilt['datetime'] <= date_range_slider_meteo[1])]
# Filter for the hours between 10 and 15
df_filtered = df_selection_meteo[(df_selection_meteo['hour'] >= date_range_slider_hours[0]) & 
                                 (df_selection_meteo['hour'] <= date_range_slider_hours[1])]

# Group by date and calculate the mean for each day
df_grouped = df_filtered.groupby(df_filtered['datetime'].dt.date)['cloudscale'].min().reset_index()
# Rename columns for clarity
df_grouped.columns = ['date', 'min_cloudscale']

# Convert date back to datetime format for plotting
df_grouped['date'] = pd.to_datetime(df_grouped['date'])

# Display the bar chart
chart_meteo = alt.Chart(df_grouped).mark_bar().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('min_cloudscale', title=f'Min cloudiness (0-9)'),
).properties(height=320)

total_reads_meteo = len(df_grouped.index)
df_unclouded_meteo = df_grouped.loc[(df_grouped['min_cloudscale'] <= 1)]
unclouded_reads_meteo = len(df_unclouded_meteo.index)
percentage_meteo = round((unclouded_reads_meteo/total_reads_meteo)*100,2)

st.altair_chart(chart_meteo.interactive(), use_container_width=True)

st.write(f"""Found **{total_reads_meteo}** total days with meteo reads!
    With **{unclouded_reads_meteo}** unclouded hours within the hour range. This means that overall about **{percentage_meteo} %** have unclouded hours within selected timerange!            
        """)

container = st.container(border=True)
container.write(f"**Conclusion**")
container.write(f"""
                High occurrence and variability of clouds in the AOI are drastically reducing succesful reads of optical imagery.
                Introducing higher cadence mitigates many issues of unsuccesful reads, but some extended intervals (multiple weeks) with cloud occurence remain in the AOI
                """)

#try:
#    m1.add_raster(raster_path, indexes=[4,3,2],layer_name='Planet')
#except ImportError as e:
#    st.write(f"Something went wrong {e}")
#m1.to_streamlit(height=600)

map = st_folium(
    m1,
    width=700, height=300,
    key="folium_map"
)

# Add the Folium map to the Streamlit app using the st_folium library
url_cbs = 'https://www.cbs.nl/nl-nl/cijfers/detail/7140gras'
st.subheader("Topic 2 : Grassland management in the Betuwe")
st.write(f"""Grass is a major **fodder** crop in the Netherlands and is utilized by livestock **grazing** or by **mowing**. 
            The [Central Bureau for Statistics (CBS)]({url_cbs}) published data on grassland mowing (see table below).
            Using this data we can estimate that traditionally on average a grass field is mowed between 2.1 to 2.85 times. However some fields will not be mowed at all due to grazing, so the numbers of 'cuts' per season will be much higher for other grassland parcels. 
            Without grazing usually 4 cuts are executed in one year. This [study](https://edepot.wur.nl/20296) also found that the ammount of cuts is also related to soiltypes; peat and clay soils have less cuts on average compared to wet and dry sandy soils. 
            The first cut of the season is much dependant on weather conditions. The temperature sum (TSum) is a good proxy to determine grassland readiness.
            In the fall and winter traditionally (after October) no mowing is performed as well due to the risk of frost damage. However this is shifting to later in the season due to the lack of frost periods induced by climate change.
            Below we will further explore the grasslands, the management and CAP related regulation in the AOI 'Betuwe'.
            """)
cbs_df = pd.read_csv("data/dataframes/Grassland_statistics.csv",delimiter=';',dtype=str)
st.table(cbs_df)

# When the user interacts with the map
# Create a map with the GeoJSON data using folium
st.write(f"""LPIS data for the AOI reveals that 53.6 percent of the area is under grassland and 42.4 is under cropland. The remaining part is under management like fallow land, wooded patches or landscape elements.
            To investigate further the grasslands in the western part of the AOI is plotted and linked to satellite reads; as such capabilities of monitoring grasslands within the CAP using EO can be explored.
            The grasslands can be subdivided in permanent grasslands, temporary grasslands and grasslands sown with a mix of seeds for agricultural purposes and nature conservation purposes.""")

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
    width=700, height=300,
    key="folium_map"
)
with st.expander("Toggle linked Sentinel-2 plot",expanded=True):
    df = load_parquet()

    gid_to_plot = 71757
    if map.get("last_object_clicked_tooltip"):
        gid_to_plot = get_gid_from_tooltip(map["last_object_clicked_tooltip"])
    if gid_to_plot is not None:
        # subselect data
        df_selection = df.loc[df['gid'] == gid_to_plot]
        #st.dataframe(data=df_selection.head(20))
        # Display line chart
        chart = alt.Chart(df_selection).mark_line(point={
        "filled": False,
        "fill": "white"
        }).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('NDVI:Q', title='NDVI'),
                    #color='genre:N'
                    ).properties(height=320)
        st.write('Chart of succesful NDVI reads by Sentinel-2')
        st.altair_chart(chart.interactive(), use_container_width=True)

with st.expander("Toggle linked Sentinel-1 plot",expanded=True):
    df_GRD = load_GRD_parquet()

    if map.get("last_object_clicked_tooltip"):
        gid_to_plot = get_gid_from_tooltip(map["last_object_clicked_tooltip"])
    if gid_to_plot is not None:
        # subselect data
        df_selection_GRD = df_GRD.loc[df_GRD['gid'] == gid_to_plot]
        
        # Melt the DataFrame to have a long format suitable for Altair
        df_melted = df_selection_GRD.melt(id_vars=['date', 'gid', 'orbit'], value_vars=['VV', 'VH'], var_name='Polarization', value_name='Value')
        #st.dataframe(data=df_melted.head(10))
        # Create the Altair chart
        chart_grd = alt.Chart(df_melted).mark_line(point={
            "filled": False,
            "fill": "white"
        }).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('Value:Q', title='Value (dB)'),
            color=alt.Color('orbit:N', title='Relative Orbit'),
            strokeDash='Polarization',  # Different lines for VV and VH
        ).properties(height=320)

        st.write('Chart of Sentinel-1 reads separated per orbit')
        st.altair_chart(chart_grd.interactive(), use_container_width=True)

container = st.container(border=True)
container.write(f"**Conclusions**")
container.markdown(
    """
    Although Sentinel-2 has a cadency of about 3 days due to overlapping tracks over the AOI there are many gaps during the season with following implications:
    - For some fields (e.g. gid 657116) mowing events can be captured shown by a significant drop in NDVI
    - No data is available in the date range from end june to end of august when often one of the mowing event takes place.
    - Data is more sparse in the winter and fall. First mowing in April/May is often not captured.

    Sentinel-1 has multiple orbits (two descending and two ascending orbits) in the AOI and reads are independent from cloud conditions 
    - Within the AOI the cadency is fairly high with 3 to 4 days between revisits
    - Comparing the data between the direction of the orbits is not directly straightforward
    - The data is not directly indicating clear mowing events; probably due to grasslands often being smaller fields and the backscatter signal has noise/speckles
    
    **OVERALL FIRST CONCLUSION**

    - **SENTINEL-2 would benefit from an increased cadency to increase the chance of a succesful capture although this is not a panacae due to cloudy periods.**
    - **Simple plotting of Sentinel-1 and Sentinel-2 timeseries will not yield in robust, fully automated monitoring of grassland management like mowing**
    - **However such plots can help to monitor certain parts of the regulations or flag fields for further investigation**
    - **In-situ data is needed to conclude which characteristics mowing events have in the reads and whether calculations exists to make Sentinel-1 reads more robust.** 
    """)

# When the user interacts with the map
# Create a map with the GeoJSON data using folium
st.write(f"""For some fields in the AOI some in-situ data on mowing and grazing exists for the year 2022. This is used to elaborate on the Sentinel-1 and Sentinel-2 reads.
""")

geojson_testfields = load_geojson_testfields()
# pre parse the mowing and grazing dates if available
mowing_dates = geojson_testfields.set_index('fid')['field_3'].apply(parse_dates).to_dict()
grazing_dates = geojson_testfields.set_index('fid')['field_5'].apply(parse_dates).to_dict()

m_tf = folium.Map(location=[sum(geojson_testfields.total_bounds[[1, 3]]) / 2, sum(geojson_testfields.total_bounds[[0, 2]]) / 2], zoom_start=12)
# add geojson and add some styling
folium.GeoJson(data=geojson_testfields,
                        name = 'Betuwe',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['fid','mowed','grazed','gid'])
                        ).add_to(m_tf)

folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m_tf)
map_tf = st_folium(
    m_tf,
    width=700, height=300,
    key="folium_map"
)

with st.expander("Toggle linked Sentinel-2 plot",expanded=True):
    df_tf = load_parquet_tf()
    fid_to_plot_tf = 121915
    if map_tf.get("last_object_clicked_tooltip"):
        fid_to_plot_tf = get_fid_from_tooltip(map_tf["last_object_clicked_tooltip"])
    if fid_to_plot_tf is not None:
        # subselect data
        df_selection_tf = df_tf.loc[df_tf['fid'] == fid_to_plot_tf]
        mowing_dates_to_plot = mowing_dates[fid_to_plot_tf]
        grazing_dates_to_plot = grazing_dates[fid_to_plot_tf]
        # combine the two lists into dataframe and add event type
        event_data = []
        # Add mowing dates to the event data
        if mowing_dates_to_plot:
            event_data.extend([{'Event Date': date, 'Event': 'Mowing'} for date in mowing_dates_to_plot])
        # Add grazing dates to the event data
        if grazing_dates:
            event_data.extend([{'Event Date': date, 'Event': 'Grazing'} for date in grazing_dates_to_plot])
        # Convert to a DataFrame
        event_df = pd.DataFrame(event_data)
        
        # Display line chart
        chart_tf = alt.Chart(df_selection_tf).mark_line(point={
        "filled": False,
        "fill": "white"
        }).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('NDVI:Q', title='NDVI'),
                    #color='genre:N'
                    ).properties(height=320)
        st.write('Chart of succesful NDVI reads by Sentinel-2')
        # add mowing and grazing dates if df is not empty
        if not event_df.empty:
            rules_mowing_grazing = alt.Chart(event_df).mark_rule().encode(
                x='Event Date:T',
                color=alt.Color('Event:N', scale=alt.Scale(domain=list(event_colors.keys()), range=list(event_colors.values())), title='Event Type'),
                #strokeDash=alt.StrokeDash('event:N', title='Event Type'),  # Dash by event type
                size=alt.value(2),  # Set line width
            )
            # update final chart
            chart_tf += rules_mowing_grazing
        # plot chart
        st.altair_chart(chart_tf.interactive(), use_container_width=True)

with st.expander("Toggle linked Sentinel-1 plot",expanded=True):
    df_GRD_tf = load_GRD_parquet_tf()
    if map_tf.get("last_object_clicked_tooltip"):
        fid_to_plot_tf = get_fid_from_tooltip(map_tf["last_object_clicked_tooltip"])
    if fid_to_plot_tf is not None:
        # subselect data
        df_selection_GRD_tf = df_GRD_tf.loc[df_GRD_tf['fid'] == fid_to_plot_tf]
        #st.dataframe(data=df_selection_GRD_tf.head(20))
        # Melt the DataFrame to have a long format suitable for Altair
        df_melted_tf = df_selection_GRD_tf.melt(id_vars=['date', 'fid', 'orbit'], value_vars=['VV', 'VH'], var_name='Polarization', value_name='Value')
        #st.dataframe(data=df_melted.head(10))
        # Create the Altair chart
        chart_grd_tf = alt.Chart(df_melted_tf).mark_line(point={
            "filled": False,
            "fill": "white"
        }).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('Value:Q', title='Value (dB)'),
            color=alt.Color('orbit:N', title='Relative Orbit'),
            strokeDash='Polarization',  # Different lines for VV and VH
        ).properties(height=320)
        #
        # Check if list_1_dates is not empty and create vertical line rules
        if len(mowing_dates_to_plot) != 0:
            rules_mowing = alt.Chart(pd.DataFrame({
                'Mowing': mowing_dates_to_plot
            })).mark_rule(color='darkgreen').encode(
                x=alt.X('Mowing:T'),
                #,
                
            )
            chart_grd_tf += rules_mowing

        if len(grazing_dates_to_plot) != 0:
            rules_grazing = alt.Chart(pd.DataFrame({
                'Grazing': grazing_dates_to_plot
            })).mark_rule(color='lightgreen').encode(
                x=alt.X('Grazing:T'),
                #,
               
            )
            chart_grd_tf += rules_grazing
        
        st.write('Chart of Sentinel-1 reads seperated per orbit')
        st.altair_chart(chart_grd_tf.interactive(), use_container_width=True)

container = st.container(border=True)
container.write(f"**Conclusions**")
container.markdown(
    """
    **The graph showing the Sentinel-2 reads and Sentinel-1 in combination with the in-situ data on mowing and grazing shows us the following.**
    - **Many mowing events are reflected by a drop in NDVI**
    - **Grazing hardly impacts the NDVI and cannot be monitored by NDVI reads**
    - **Not all drops in NDVI in the graphs are related to mowing, but are rather related to natural processes like drought (see especially the period from August 10th to September 1st)**
    - **The analysis ready sigma0 Sentinel-1 VV and VH plots do not seem suitable to indicate mowing events. Probably this is also related to the structure of the grass not changing that much after mowing** 
    - **The question remains whether the radar data can be manipulated or using the complex values to generate robust indices.**
    """)
url_paper_grassland_mowing = 'https://doi.org/10.1016/j.rse.2023.113680'
st.write(f"""For Sentinel-1 reads the so-called Radar Vegetation Index (see formula below) and the ratio between VV and VH can be useful to better discriminate vegetational patterns.
See example this paper on [Grassland mowing event detection]({url_paper_grassland_mowing}). Also the coherence between two reads can be a useful metric to flag changes. The higher the coherence the lower the changes measured. With events like mowing a dip in coherence is expected. 
The plots below shows the plot of RVI and VV/VH ratio. The second plot shows the coherence of images with 12 days apart during a large part of the growing season. It is good to note that since 2021 one Sentinel-1 sensor is available and therefore the cadency of the coherence product is reduced from 6 to 12 days. Also coherence products are not readily available for these seasons on Dataspace providers, therefore the graph is showing self-processed coherence reads and is limited to a part of the season (march - july).
""")
st.latex(r'''
    RVI = \frac{4 \cdot V H}{V H + V V}
    ''')

with st.expander("Toggle indices plot from Sentinel-1 reads",expanded=True):
    if map_tf.get("last_object_clicked_tooltip"):
        fid_to_plot_tf = get_fid_from_tooltip(map_tf["last_object_clicked_tooltip"])
    if fid_to_plot_tf is not None:
        # subselect data
        df_selection_GRD_tf = df_GRD_tf.loc[df_GRD_tf['fid'] == fid_to_plot_tf]
        df_selection_GRD_tf['VV/VH'] = df_selection_GRD_tf['VV']/df_selection_GRD_tf['VH']
        min_RVI = df_selection_GRD_tf['RVI'].values.min()
        max_RVI = df_selection_GRD_tf['RVI'].values.max()
        #st.dataframe(data=df_selection_GRD_tf.head(20))
        # Melt the DataFrame to have a long format suitable for Altair
        df_melted_tf_rvi = df_selection_GRD_tf.melt(id_vars=['date', 'fid', 'orbit'], value_vars=['RVI','VV/VH'], var_name='Indices', value_name='Value')
        #st.dataframe(data=df_melted.head(10))
        # Create the Altair chart
        base_chart_grd_tf_rvi = alt.Chart(df_melted_tf_rvi).mark_line(point={
            "filled": False,
            "fill": "white"
        }).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('Value:Q',
            scale = alt.Scale(domain=[min_RVI,max_RVI])), 
            #scale=alt.Scale(domain=[min_RVI, max_RVI])), 
            color=alt.Color('orbit:N', title='Relative Orbit'),
            strokeDash='Indices',
        ).properties(height=320).interactive()
        #
        # Check if list_1_dates is not empty and create vertical line rules
        if len(mowing_dates_to_plot) != 0:
            rules_mowing = alt.Chart(pd.DataFrame({
                'Mowing': mowing_dates_to_plot
            })).mark_rule(color='darkgreen').encode(
                x=alt.X('Mowing:T'),
                #,
                
            )
            base_chart_grd_tf_rvi += rules_mowing

        if len(grazing_dates_to_plot) != 0:
            rules_grazing = alt.Chart(pd.DataFrame({
                'Grazing': grazing_dates_to_plot
            })).mark_rule(color='lightgreen').encode(
                x=alt.X('Grazing:T'),
                #,
               
            )
            base_chart_grd_tf_rvi += rules_grazing
        st.write('Chart of Sentinel-1 RVI reads seperated per orbit')
        st.altair_chart(base_chart_grd_tf_rvi.interactive(), use_container_width=True)

df_COH_tf = load_coh_csv()
with st.expander("Toggle coherence plot from Sentinel-1 reads",expanded=True):
    if map_tf.get("last_object_clicked_tooltip"):
        fid_to_plot_tf = get_fid_from_tooltip(map_tf["last_object_clicked_tooltip"])
    if fid_to_plot_tf is not None:
        # subselect data
        df_selection_COH_tf = df_COH_tf.loc[df_COH_tf['fid'] == fid_to_plot_tf]
        
        #min_COH = df_selection_COH_tf['RVI'].values.min()
        #max_COH = df_selection_COH_tf['RVI'].values.max()
        #st.dataframe(data=df_selection_GRD_tf.head(20))
        # Melt the DataFrame to have a long format suitable for Altair
        df_melted_tf_COH = df_selection_COH_tf.melt(id_vars=['fid','field_2','field_3','field_4','field_5','field_7','gid','landgebrui','gws_gewas','gewascode','area','mowed','grazed','geometry'],
        var_name='coherence_identifier', value_name='COH12')
        
        # Extracting VV/VH, Date, IW, and Orbit number from the 'coherence_type' column
        df_melted_tf_COH[['Polarization', 'date_range', 'IW', 'Relative Orbit']] = df_melted_tf_COH['coherence_identifier'].str.extract(
        r'(cohvv|cohvh)_(\d+T\d+_\d+T\d+)_IW(\d+)_(\w+)'
        )
        # parse to date
        df_melted_tf_COH['date'] = pd.to_datetime(df_melted_tf_COH['date_range'].str.split('_').str[-1].str[:8])
        # drop na if date cannot be parsed
        df_melted_tf_COH.dropna(subset=['date'], inplace=True)
        # change naming of cohvv to VV using mapping
        df_melted_tf_COH['Polarization'] = df_melted_tf_COH['Polarization'].map(coh_mapping)
        #df_melted_tf_COH = df_melted_tf_COH.convert_dtypes(infer_objects=True)
        #st.dataframe(df_melted_tf_COH)
        # get columntypes for debugging
        #st.write(df_melted_tf_COH.dtypes)
        #st.write(df_melted_tf_COH['date'].values)
        #st.dataframe(data=df_melted.head(10))
        # Create the Altair chart
        base_chart_COH_tf = alt.Chart(df_melted_tf_COH).mark_line(point={
            "filled": False,
            "fill": "white"}).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('COH12:Q',scale = alt.Scale(domain=[40,110])),
            #scale=alt.Scale(domain=[min_RVI, max_RVI])), 
            color=alt.Color('Relative Orbit:N', title='Relative Orbit'),
            strokeDash='Polarization:N',
            detail='IW:N',
            
        ).properties(height=320).interactive()
        #
        # Check if list_1_dates is not empty and create vertical line rules
        if len(mowing_dates_to_plot) != 0:
            rules_mowing = alt.Chart(pd.DataFrame({
                'Mowing': mowing_dates_to_plot
            })).mark_rule(color='darkgreen').encode(
                x=alt.X('Mowing:T'),
                #,
                
            )
            base_chart_COH_tf += rules_mowing

        if len(grazing_dates_to_plot) != 0:
            rules_grazing = alt.Chart(pd.DataFrame({
                'Grazing': grazing_dates_to_plot
            })).mark_rule(color='lightgreen').encode(
                x=alt.X('Grazing:T'),
                #,
               
            )
            base_chart_COH_tf += rules_grazing
        st.write('Chart of Sentinel-1 COH reads seperated per relative orbit and IW')
        st.altair_chart(base_chart_COH_tf.interactive(), use_container_width=True)

container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(
    """
    **The plot of the RVI (and the VV/VH below) does not show clear dips, peaks or other features around mowing events. Therefore it can be concluded that:** 
    - **The RVI and the VV/VH are not suitable or not robust enough to indicate mowing and/or grazing events**
    - **The indices do not add any discriminative power for grassland monitoring.**
    
    **The plot of the COH12 do show lower coherence around the mowing dates and an increasing coherence between mowing dates. Therefore it can be concluded that:** 
    - **Coherence seems to be a usefull metric for event detection like mowing**
    - **A increased cadency (e.g. 6 days) will likely show clearer dips**
    - **Coherence reads are probably more robust with increased resolution or larger fields compared to the size of grassland fields in the AOI**
    - **Coherence also drops to phenological changes during the season and field circumstances like moisture on the leaves, making the methodolgy less robust** 
    """)

url_planet_fusion_white_paper = r"https://learn.planet.com/rs/997-CHH-265/images/Planet%20Fusion%20Monitoring%20Datasheet_Letter_Web.pdf"
st.write(f"""In the previous section one of the conclusions was that Sentinel-2 timeseries had gaps preventing a clear determination of dips in the NDVI indicating mowing events.
A solution to circumvent this problem of cadency is to use optical sensors in a large constellation like the Planet superdoves, Pleiades NEO or Superview NEO are offering. 
Such constellations have (sub)daily revisit times increasing the chance of succesful reads. The succesfulness of this approach is explored in the topic on cloudiness using meteo reads.
An additional approach is to use daily revisit images, in combination with free imagery from e.g. the Sentinel-2 and Landsat sensors and use Machine Learning to predict/interpolate pixels for clouded days to ensure a continuous daily monitoring. This approach is explained in [this white paper]({url_planet_fusion_white_paper}).
Below a plot is given to explore the usefullness and accuracy of such approaches for grassland monitoring in the AOI. Fields with additional blue shading of the polygons are fields with in-situ mowing and grazing data""")

pf_fields = load_planet_fusion_csv()

m_pf = folium.Map(location=[sum(pf_fields.total_bounds[[1, 3]]) / 2, sum(pf_fields.total_bounds[[0, 2]]) / 2], zoom_start=12)
# add geojson and add some styling
folium.GeoJson(data=geojson_testfields,
                        name = 'In-situ fields',
                        tooltip = folium.GeoJsonTooltip(fields=['mowed','grazed'])
                        ).add_to(m_pf)
folium.GeoJson(data=pf_fields,
                        name = 'Betuwe',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m_pf)

folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m_pf)
map_pf = st_folium(
    m_pf,
    width=700, height=300,
    key="folium_map"
)

# pre parse the mowing and grazing dates if available
mowing_dates_pf = geojson_testfields.set_index('gid')['field_3'].apply(parse_dates).to_dict()
grazing_dates_pf = geojson_testfields.set_index('gid')['field_5'].apply(parse_dates).to_dict()

with st.expander("Toggle linked interpolated fusion product plot",expanded=True):
    gid_to_plot_pf = 657116
    if map_pf.get("last_object_clicked_tooltip"):
        gid_to_plot_pf = get_gid_from_tooltip(map_pf["last_object_clicked_tooltip"])
    if gid_to_plot_pf is not None:
        # subselect data
        df_selection_pf = pf_fields.loc[pf_fields['gid'] == gid_to_plot_pf]
        # subselect only the date columns holding the ndvi reads
        date_columns = df_selection_pf.columns[8:-2]  #First columns are not dates and last two also not
        ndvi_reads = df_selection_pf[date_columns]
        # melt the dataframe
        df_ndvi_pf = ndvi_reads.reset_index().melt(id_vars='index', var_name='Date', value_name='NDVI')
        # plot in a graph if available
        if gid_to_plot_pf in mowing_dates_pf.keys():
            mowing_dates_to_plot = mowing_dates_pf[gid_to_plot_pf]
        else: mowing_dates_to_plot = []
        if gid_to_plot_pf in grazing_dates_pf.keys():
            grazing_dates_to_plot = grazing_dates_pf[gid_to_plot_pf]
        else: grazing_dates_to_plot = []
        # combine the two lists into dataframe and add event type
        event_data = []
        # Add mowing dates to the event data
        if mowing_dates_to_plot:
            event_data.extend([{'Event Date': date, 'Event': 'Mowing'} for date in mowing_dates_to_plot])
        # Add grazing dates to the event data
        if grazing_dates:
            event_data.extend([{'Event Date': date, 'Event': 'Grazing'} for date in grazing_dates_to_plot])
        # Convert to a DataFrame
        event_df = pd.DataFrame(event_data)
        
        # Display line chart
        chart_pf = alt.Chart(df_ndvi_pf).mark_line(point={
        "filled": False,
        "fill": "white"
        }).encode(
                    x=alt.X('Date:T', title='Date'),
                    y=alt.Y('NDVI:Q', title='NDVI'),
                    #color='genre:N'
                    ).properties(height=320)
        st.write('Chart of NDVI from interpolated fusion product')
        # add mowing and grazing dates if df is not empty
        if not event_df.empty:
            rules_mowing_grazing = alt.Chart(event_df).mark_rule().encode(
                x='Event Date:T',
                color=alt.Color('Event:N', scale=alt.Scale(domain=list(event_colors.keys()), range=list(event_colors.values())), title='Event Type'),
                #strokeDash=alt.StrokeDash('event:N', title='Event Type'),  # Dash by event type
                size=alt.value(2),  # Set line width
            )
            # update final chart
            chart_pf += rules_mowing_grazing
        # plot chart
        st.altair_chart(chart_pf.interactive(), use_container_width=True)
container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(
    """
    **The above plot clearly shows the added value of this methodology**
    - **Using daily revisit cadency and incorporating imagery from free-of-charge sensor adds additional reads compared to using only Sentinel-2**
    - **Machine learning can be leveraged to interpolate the timeseries**
    - **It allows for smooth timeseries and clearer determination of dips indicating mowing events**
    - **Not all dips are explained by mowing events. Natural drying of grass is also a reason for NDVI dips.**
    """)

df_conv_pf = load_conv_csv()
# calculate mean of SD for each date, each conv and each gws_gewas type
df_mean_gws_melt = df_conv_pf.melt(id_vars=['index','gid','landgebrui','gws_gewas','gewascode','ptype','area','geometry'],
        var_name='conv_identifier', value_name='Mean per crop SD')
# seperate date and convolution
df_mean_gws_melt[['Convolution', 'Date']] = df_mean_gws_melt['conv_identifier'].str.extract(
        r'(\w+)_(\d+)'
        )
# parse to date
df_mean_gws_melt['date'] = pd.to_datetime(df_mean_gws_melt['Date'])
# Now group by gws_gewas, date, and convolution to get the mean
# Convert the 'read_value' column to numeric, coercing errors to NaN
df_mean_gws_melt['Mean per crop SD'] = pd.to_numeric(df_mean_gws_melt['Mean per crop SD'], errors='coerce')
df_mean_gws = df_mean_gws_melt.groupby(['gws_gewas', 'date', 'Convolution'])['Mean per crop SD'].mean().reset_index()
st.dataframe(df_mean_gws)
# instantiate altair chart
# add means per gws categories here
mean_chart = alt.Chart(df_mean_gws).mark_line().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('Mean per crop SD:Q'),
    color=alt.Color('gws_gewas:N', title='Crop type').scale(domain=list(color_dict.keys())[:4], range=list(color_dict.values())[:4]),
    strokeDash=alt.StrokeDash('Convolution:N', title='Convolution'),
)
# rename
with st.expander("Toggle standard deviation convolution plot from RadarSat-2 reads",expanded=True):
    gid_to_plot_pf = 657116
    if map_pf.get("last_object_clicked_tooltip"):
        gid_to_plot_pf = get_gid_from_tooltip(map_pf["last_object_clicked_tooltip"])
    if gid_to_plot_pf is not None:
        # subselect data
        df_selection_conv_pf = df_conv_pf.loc[df_conv_pf['gid'] == gid_to_plot_pf]
        
        #min_COH = df_selection_COH_tf['RVI'].values.min()
        #max_COH = df_selection_COH_tf['RVI'].values.max()
        #st.dataframe(data=df_selection_GRD_tf.head(20))
        # Melt the DataFrame to have a long format suitable for Altair
        df_melted_pf_conv = df_selection_conv_pf.melt(id_vars=['gid','landgebrui','gws_gewas','gewascode','ptype','area','geometry'],
        var_name='conv_identifier', value_name='Mean SD')
        
        # Extracting VV/VH, Date, IW, and Orbit number from the 'coherence_type' column
        df_melted_pf_conv[['Convolution', 'Date']] = df_melted_pf_conv['conv_identifier'].str.extract(
        r'(\w+)_(\d+)'
        )
        #st.dataframe(df_melted_pf_conv.head(10))
        # parse to date
        df_melted_pf_conv['date'] = pd.to_datetime(df_melted_pf_conv['Date'])
        # drop na if date cannot be parsed
        df_melted_pf_conv.dropna(subset=['Date'], inplace=True)
        # Create the Altair chart
        base_chart_conv_pf = alt.Chart(df_melted_pf_conv).mark_line(point={
            "filled": False,
            "fill": "white"}).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('Mean SD:Q'),#,scale = alt.Scale(domain=[40,110])),
            #scale=alt.Scale(domain=[min_RVI, max_RVI])), 
            color=alt.Color('Convolution:N', title='Convolution'),
            #strokeDash='Polarization:N',
            #detail='IW:N',
            
        )
         
        # update final chart
        #base_chart_conv_pf + mean_chart
        st.write('Chart of RadarSat-2 standard deviation reads seperated by convolution size')
        st.altair_chart(alt.layer(base_chart_conv_pf,mean_chart).properties(height=320).interactive(), use_container_width=True)


st.subheader("Topic 3 : Bufferstrips in the AOI the Betuwe")
st.write(f"""
**Buffer strips** are designated non-productive areas surrounding the main crop on the edges of the parcels with different management and/or landcover. 
On buffer strips typically no use of agro-chemicals and manure application is allowed. Beside the management also the landcover can be distinct; this can be cover crops like grass, herb-rich mixtures or flower borders. 
The rationale to have buffer strips are various from protection to bio-diversity enhancement. Protection often entails strips between the crops and waterways to prevent leaching of agro-chemicals and excess nutrients from manure or other fertilizer application. 
Bio-diversity enhancement entails e.g. the diversification of landcover, leaving land fallow, creating foraging strips for birds and sanctuaries for insects.
""")
st.write(f"""
The **obligatory** buffer strips within the **CAP** are related to **water protection** and **manure placement directives**. Depending on the waterbody type (related to width, depth, water throughput and its vulnerability) and crop type a certain distance should be respected excluding the sloping part. 
The buffer distances are 5, 3 or 1 meter wide. Crops associated with high agro-chemical use or side-way spraying like fruit trees have a large buffer strip of 5 meter. This is especially relevant for this AOI since a lot of fruit is produced in this region.""")
st.write(f"""
 Buffer strips can also be created to fulfill the requirement of leaving 4% fallow of total parcels under control of the farmer. With buffer strips we can distinguish **managed** and **unmanaged** strips where in the managed strips a certain crop type or mixture is sown in deliberately while the unmanaged bufferstrips has spontaneous vegetation.
 Below we will explore some raster and LPIS data to check how bufferstrips can be monitored and how this relates to cadency of EO.
 It is good to note that because of the scale of the bufferstrips (1-5 meter) the EO data used will be Very High Resolution (VHR) imagery with a sub-meter resolution like Pleiades NEO and SuperView NEO. Besides spaceborn source also aerial imagery is a good source of high resolution data""")

bufferstrip_fields = load_geojson_bufferstrips()
#m_bs = folium.Map(location=[sum(bufferstrip_fields.total_bounds[[1, 3]]) / 2, sum(bufferstrip_fields.total_bounds[[0, 2]]) / 2], zoom_start=12)
m_bs = folium.Map(location=[sum(bufferstrip_fields.total_bounds[[1, 3]]) / 2, sum(bufferstrip_fields.total_bounds[[0, 2]]) / 2], zoom_start=16)

# add ortho aerial imagery
folium.raster_layers.WmsTileLayer(url=r'https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
                layers = '2023_orthoHR',
                transparent = True, 
                control = True,
                fmt="image/jpeg",
                name = 'Aerial Image Winter 2023 8cm RGB',
                attr = 'PDOK / opendata.beeldmaterial.nl',
                overlay = True,
                show = True,
                #CRS = 'EPSG:4326',
                ).add_to(m_bs)

folium.raster_layers.WmsTileLayer(url=r'https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
                layers = '2023_ortho25',
                transparent = True, 
                control = True,
                fmt="image/jpeg",
                name = 'Aerial Image Summer 2023 25cm RGB',
                attr = 'PDOK / opendata.beeldmaterial.nl',
                overlay = True,
                show = True,
                #CRS = 'EPSG:4326',
                ).add_to(m_bs)

folium.GeoJson(data=bufferstrip_fields,
                        name = 'Betuwe LPIS declarations',
                        style_function=style_function_bufferstrips,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode']),
                                                ).add_to(m_bs)
control = folium.LayerControl(collapsed=False)
#folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m_pf)
map_bs = st_folium(
    m_bs,
    width=700, height=300,
    key="folium_map",
    layer_control=control
)
st.write("Browsing through the map and checking both the winter as summer images often is sufficient to check the declaration of bufferstrips and the area between waterbodies and fruit plantations.Below two cases are presented as examples.")
st.image(["data/images/CorrectDecl_1.png","data/images/CorrectDecl_2.png"], width=350, caption=["Winter image showing correct delineation of bufferstrip and presence of vegetation","Summer image showing correct delineation of bufferstrip and presence of vegetation"])
st.image(["data/images/ProbWrongDecl_1.png","data/images/ProbWrongDecl_2.png"],width=350, caption=["Winter image showing incorrect delineation of fallow land and no vegetation","Winter image showing incorrect delineation of fallow land and no vegetation"])
url_nso = "https://www.spaceoffice.nl/en/"
url_sattelietdataportaal = "https://viewer.satellietdataportaal.nl/"
st.write(f"""In order to investigate more in depth the field which is probably wrongly declared as fallow land more in depth we can visually inspect available VHR. The [Netherlands Space Office]({url_nso}) provides a [sattelite imagery portal]({url_sattelietdataportaal}) for Dutch users including Pleiades NEO and SuperView NEO. 
For the AOI Betuwe in 2023 43 images are available. Please note that the footprints of these images do not overlap the AOI entirely and can include some cloudcover. For the field to investigate there are 4 cloudfree images available through the entire year (April 30th, May 14th, June 3rd and September 8th). These images are displayed below as static images to support that the declaration is not correct.
""")
st.image(["data/images/ProbWrongDecl_NEO4.png","data/images/ProbWrongDecl_NEO3.png"], width=350, caption=["Pleiades NEO captured April 30th","Pleiades NEO captured May 14th"])
st.image(["data/images/ProbWrongDecl_NEO2.png","data/images/ProbWrongDecl_NEO1.png"],width=350, caption=["Pleiades NEO captured June 3d","SuperView NEO captured September 8th"])

st.write(f"""In order to make even more clear whether vegetation is present the Infra-red channel of the VHR can be leveraged""")

st.image(["data/images/ProbWrongDecl_NEO4_IRG.png","data/images/ProbWrongDecl_NEO3_IRG.png"], width=350, caption=["Pleiades NEO captured April 30th","Pleiades NEO captured May 14th"])
st.image(["data/images/ProbWrongDecl_NEO2_IRG.png","data/images/ProbWrongDecl_NEO1_IRG.png"],width=350, caption=["Pleiades NEO captured June 3d","SuperView NEO captured September 8th"])

container = st.container(border=True)
container.write(f"**Conclusion on field investigation**")
container.markdown("""
    The images clearly indicate that this bufferstrip is most likely not managed as declared (fallow land)
    - At least up to June there is no vegetation present
    - On the last image (Sept 8th) there is no distinction visible between the main crop and the bufferstrip
    """)
container = st.container(border=True)
container.write(f"**General conclusion on bufferstrips**")
container.markdown(
    """
    **For monitoring the bufferstrip we can conclude:**
    - **Since many bufferstrip need to be present either the whole year round or a significant time of the year cadency is not of utmost importance**
    - **Sub-meter resolution of EO imagery is of utmost importance, because buffer strips are narrow**
    - **A (guaranteed cloud-free) aerial image in each growing season with super high resolution (8cm-25cm) brings much added value for the CAP, to enable inspection of parcel delineations**
    - **VHR like Pleiades NEO and SuperView NEO are valuable for in-season checking and have added value by capturing the Near-Infrared values of crops**
    """)

