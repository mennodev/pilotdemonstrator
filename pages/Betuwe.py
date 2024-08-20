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
    'Grasland, tijdelijk': 'Grassland, temporary'
}
# Color dictionary
color_dict = {
    'Grasland, blijvend': 'green',
    'Grasland, natuurlijk. Met landbouwactiviteiten.': 'darkgreen',
    'Agrarisch natuurmengsel': 'yellow',
    'Grasland, tijdelijk': 'orange'
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
    return df

def load_meteo_data_daytime():
    df = pd.read_csv("data/dataframes/meteo_daytime.txt",delimiter=',',parse_dates=['datetime'])
    return df

def load_parquet():
    df = pd.read_parquet("data/dataframes/NDVI_GrasslandsParcels_Betuwe2023_pq.parquet", engine='pyarrow')
    return df

def load_GRD_parquet():
    df = pd.read_parquet("data/dataframes/GRD_GrasslandsParcels_Betuwe2023_pq.parquet", engine='pyarrow')
    return df

def load_parquet_tf():
    df = pd.read_parquet("data/dataframes/NDVI_GrasslandsParcels_Betuwe2022_pq.parquet", engine='pyarrow')
    return df

def load_GRD_parquet_tf():
    df = pd.read_parquet("data/dataframes/GRD_GrasslandsParcels_Betuwe2022_pq.parquet", engine='pyarrow')
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

def load_planet_fusion_csv():
    df = pd.read_csv("data/dataframes/PlanetFusionNDVI.csv")
    # parse geometries for geopandas using shapely wkt
    df['geometry'] = df['geometry'].apply(wkt.loads)
    # make gdf with geopandas
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
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

st.altair_chart(chart.interactive(), use_container_width=True)
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

st.altair_chart(chart_meteo.interactive(), use_container_width=True)
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
st.write(f"""LPIS data for the AOI reveals that 53.6 percent of the area is under grassland and 42.4 is under cropland. The remaining part is under management like fallow land, wooded patches or landscape elements.
            To investigate further the grasslands in the western part of the AOI is plotted and linked to satellite reads to explore capabilities of monitoring grasslands within the CAP using EO.
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
    width=900, height=600,
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
        st.write('Chart of succesfull NDVI reads by Sentinel-2')
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
            color=alt.Color('orbit:N', title='Orbit Number'),
            strokeDash='Polarization',  # Different lines for VV and VH
        ).properties(height=320)

        st.write('Chart of Sentinel-1 reads seperated per orbit')
        st.altair_chart(chart_grd.interactive(), use_container_width=True)

container = st.container(border=True)
container.write(f"**Conclusions**")
container.markdown(
    """
    Although Sentinel-2 has a cadency of 5 days within the AOI there are many gaps during the season with following implications:
    - For some fields (e.g. gid 657116) mowing events can be captured shown by a significant drop in NDVI
    - No data is available in the crucial date range from end june to end of august when often one of the mowing event takes place.
    - Data is more sparse in the winter and fall. First mowing in April/May is often not captured.

    Sentinel-1 has multiple orbits in the AOI and reads are independent from cloud conditions. 
    - Within the AOI the cadency is 3 to 4 days
    - Comparing the data between orbits is not directly straightforward
    - The data is not robust enough to be used to capture clear mowing events
    
    **OVERALL FIRST CONCLUSION**

    - **SENTINEL-2 would benefit from an increased cadency to increase the chance of a succesfull capture although this is not a panacae due to cloudy periods.**
    - **Simple plotting of Sentinel-1 and Sentinel-2 timeseries will not yield in robust monitoring of grassland management like mowing.**
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
    width=900, height=600,
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
        st.write('Chart of succesfull NDVI reads by Sentinel-2')
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
            color=alt.Color('orbit:N', title='Orbit Number'),
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
    - **Not all drops in NDVI in the graphs are related to mowing, but sometimes related to natural processes like drought (see especially period from August 10th to September 1st)**.
    - **The sigma0 Sentinel-1 VV and VH plots are not suitable at all to indicate mowing events. The question is whether the radar data can be manipulated to generate robust indices.**
    """)
url_paper_grassland_mowing = 'https://doi.org/10.1016/j.rse.2023.113680'
st.write(f"""For Sentinel-1 reads the so-called Radar Vegetation Index (see formula below) and the ratio between VV and VH can be useful to better discriminate vegetational patterns.
See example this paper on [Grassland mowing event detection]({url_paper_grassland_mowing}). The below plot shows the plot of RVI.
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
            color=alt.Color('orbit:N', title='Orbit Number'),
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
container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(
    """
    **The plot of the RVI (and the VV/VH below) does not show clear dips, peaks or other features around mowing events. Therefore it can be condluded that:** 
    - **The RVI and the VV/VH are not suitable or not robust enough to indicate mowing and/or grazing events**
    - **The indices do not add any discrimination power for grassland monitoring.**
    """)
url_planet_fusion_white_paper = r"https://learn.planet.com/rs/997-CHH-265/images/Planet%20Fusion%20Monitoring%20Datasheet_Letter_Web.pdf"
st.write(f"""In the previous section one of the conclusions was that Sentinel-2 timeseries had gaps preventing a clear determination of dips in the NDVI indicating mowing events.
A solution to circumvent this problem of cadency is to use optical sensors in a large constellation like the Planet superdoves, Pleiades NEO or Superview NEO. 
Such constellations have (sub)daily revisit times increasing the chance of succesfull reads. The succesfullness of this approach is explored in the topic on cloudliness using meteo reads.
An additional approach is to use daily revisit images, combine these with free imagery from e.g. the Sentinel-2 and Landsat sensors and use Machine Learning to predict/interpolate pixels for clouded days to ensure a continuous daily monitoring. This approach is explained in [this white paper]({url_planet_fusion_white_paper}).
Below a plot is given to explore the usefullness and accuracy of such approaches for grassland monitoring in the AOI""")

pf_fields = load_planet_fusion_csv()

m_pf = folium.Map(location=[sum(pf_fields.total_bounds[[1, 3]]) / 2, sum(pf_fields.total_bounds[[0, 2]]) / 2], zoom_start=12)
# add geojson and add some styling
folium.GeoJson(data=geojson_testfields,
                        name = 'Betuwe',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m_pf)

folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m_pf)
map_pf = st_folium(
    m_pf,
    width=900, height=600,
    key="folium_map"
)

with st.expander("Toggle linked interpolated fusion product plot",expanded=True):
    gid_to_plot_pf = 71757
    if map_pf.get("last_object_clicked_tooltip"):
        gid_to_plot_pf = get_gid_from_tooltip(map_pf["last_object_clicked_tooltip"])
    if gid_to_plot_pf is not None:
        # subselect data
        df_selection_pf = pf_fields.loc[pf_fields['gid'] == gid_to_plot_pf]
        # Extract the columns that contain the dates and NDVI values
        date_columns = df_selection_pf.columns[7:]  # Assuming the first six columns are not dates
        # Convert the date columns to datetime objects
        dates = pd.to_datetime(date_columns, format='%d/%m/%Y')
        # Extract the columns that contain the dates and NDVI values
        ndvi_values = df_selection_pf[date_columns].values
        st.write(ndvi_values)