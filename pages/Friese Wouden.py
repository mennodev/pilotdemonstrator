import altair as alt
import pandas as pd
import geopandas as gpd
import streamlit as st
from modules.nav import Navbar
from streamlit_folium import folium_static
import folium
from streamlit_folium import st_folium
from modules.nav import Navbar
import leafmap.foliumap as leafmap
from datetime import datetime
from shapely import wkt
# setup page config using modules
Navbar()

st.title("Pilot demonstrator AOI Friese Wouden")

st.header("Demonstrator focusing on landscape features in the CAP and relation to cadency")
st.write(
    """
    Below you find different blocks of data visualization developed in the pilot demonstrator exploring different topics. 
    """
)
# Helper functions

# Translation dictionary
translation_dict = {
    "Sloot": "Water carying ditch",
    "Houtwal en houtsingel": "Wooded bank and tree row",
    "Stroken wild gras": "Strips of wild grass",
    "Water, overig": "Water, other",
    "Poel en klein historisch water": "Pond and small historic water",
    "Rietzoom en klein rietperceel": "Reed edge and small reed parcel",
    "Elzensingel": "Alder row",
    "Landschapselement, overig": "Landscape element, other",
    "Ruigtes op landbouwpercelen": "Rough areas on agricultural fields",
    "Boomgroep": "Group of trees",
    "Bossingel": "Tree belt",
    "Bosje": "Small wood",
    "Natuurvriendelijke oever": "Nature-friendly bank",
    "Knip- of scheerheg": "Pruned or trimmed hedge",
    "Schouwpad": "Inspection path",
    "Laan": "Tree-lined avenue",
    "Struweelrand": "Scrub edge",
    "Struweelhaag": "Scrub hedge",
    "Hakhoutbosje": "Coppice",
    "Griendje": "Willow coppice",
    "Hoogstamboomgaard": "High-stem orchard",
    "Schurvelingen en zandwallen": "Earth banks and sand walls",
    "Voederhaag": "Feed hedge"
}
# Color dictionary
color_dict = {
    "Sloot": "blue",
    "Houtwal en houtsingel": "darkgreen",
    "Stroken wild gras": "khaki",
    "Water, overig": "LightBlue",
    "Poel en klein historisch water": "Navy",
    "Rietzoom en klein rietperceel": "Orange",
    "Elzensingel": "LightGreen",
    "Landschapselement, overig": "LightSeeGreen",
    "Ruigtes op landbouwpercelen": "Moccasin",
    "Boomgroep": "OliveDrab",
    "Bossingel": "Olive",
    "Bosje": "ForestGreen",
    "Natuurvriendelijke oever": "Teal",
    "Knip- of scheerheg": "YellowGreen",
    "Schouwpad": "SandyBrown",
    "Laan": "Sienna",
    "Struweelrand": "PeachPuff",
    "Struweelhaag": "PaleGoldenRod",
    "Hakhoutbosje": "Maroon",
    "Griendje": "DarkTurquoise",
    "Hoogstamboomgaard": "DarkKhaki",
    "Schurvelingen en zandwallen": "yellow",
    "Voederhaag": "DarkCyan"
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
    df['management'] = df['gws_gewas'].map(translation_dict)
    df['color'] = df['gws_gewas'].map(color_dict)
    return df

def load_geojson_LE():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/LPIS_Grasslands.geojson")
    # translate to English
    gdf['management'] = gdf['gws_gewas'].map(translation_dict)
    gdf['color'] = gdf['gws_gewas'].map(color_dict)
    # Convert the GeoDataFrame to a DataFrame
    #df = pd.DataFrame(gdf)
    return gdf

def load_geojson_FW():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/AOI_FrieseWouden.geojson")
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

def style_function_AOI(x):
    """
    Use color column to assign color
    """
    return {"color":'blue', "weight":1, "fillOpacity":0.0}

# Add the Folium map to the Streamlit app using the st_folium library
url_benefits_lf = 'https://publications.jrc.ec.europa.eu/repository/bitstream/JRC128297/JRC128297_01.pdf'
container = st.container(border=True)
container.write(f"**Defenition of agricultural landscape features**")
container.markdown(f"""Landscape features are small fragments of 
non-productive natural or semi-natural vegetation in agricultural landscape which provide 
ecosystem services and support for biodiversity ([source: Technical Report JRC]({url_benefits_lf}))""")

ammount_dict = {"Water carying ditch":"50379",
"Wooded bank and tree row":"5191",
"Strips of wild grass":"529",
"Water, other":"497",
"Pond and small historic water":"461",
"Reed edge and small reed parcel":"225",
"Alder row":"6712",
"Landscape element, other":"513",
"Rough areas on agricultural fields":"173",
"Group of trees":"113",
"Tree belt":"63",
"Small wood":"208",
"Nature-friendly bank":"83",
"Pruned or trimmed hedge":"41",
"Inspection path":"14",
"Tree-lined avenue":"108",
"Scrub edge":"17",
"Scrub hedge":"34",
"Coppice":"35",
"Willow coppice":"1",
"High-stem orchard":"2",
"Earth banks and sand walls":"3",
"Feed hedge":"1"}

df_LE_ammounts = pd.DataFrame(list(ammount_dict.items()), columns=['LF type','Occurence'])

container = st.container(border=True) 
container.write(f"**Types of agricultural landscape features**")
container.markdown(f"""Agricultural landscape features in the context of EU are:
        - 'Blue' features:
        + historical ponds
        + water carying ditches
        + springs
        + historic canal network 
        - 'Green' features:
        + hedges
        + trees in line, grouped or isolated
        + planted areas
        + field margins
        - 'Grey' features:
        + stone/earth walls
        + terraces
        """)
st.write("Within the Dutch context not all landscape features are relevant and included as such in the CAP regulations. Since 2023 landscape features are included in the subsidy scheme and farmers need to declare those elements. This also mean that the LPIS is extended with many more polygons delineating the features. For example in the AOI there are about 116K parcels of which 65,4K are landscape elements")
container = st.container(border=True) 
container.write(f"**Types and occurence frequency of agricultural landscape features in the AOI**")
container.table(df_LE_ammounts,hide_index=True)
st.write("From the table it is clear that water carying ditches are dominant. Also within the AOI almost all types of LF possible within the Dutch CAP are present apart from windhedge in orchards, earthen walls and terraces with shrubs. The latter only exists in province Limburg at some sloping terrains")
st.write("To get an overview of landscape features a subset of the AOI is shown in the map below")
LE_geojson = load_geojson_LE()
FW_geojson = load_geojson_FW()
st.write("""To focus on crops which can be sown as catch crops a selection is made from the LPIS data and below the 126 selected fields are plotted. 
Please note that these crops presented here are a main crop (many winter wheats) or used as a fallow crop. The open source LPIS data do not store the catch crops planted, so the fields primarily serve as a examples of crop types used in the AOI eligible as a catch crop""")

m = folium.Map(location=[sum(LE_geojson.total_bounds[[1, 3]]) / 2, sum(LE_geojson.total_bounds[[0, 2]]) / 2], zoom_start=12)
# add geojson and add some styling
# add geojson and add some styling
folium.GeoJson(data=geojson_FW,
                        name = 'AOI Friese Wouden',
                        style_function=style_function_AOI,
                        #tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)

folium.GeoJson(data=LE_geojson,
                        name = 'Landscape Features in NOP',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)
# Set the basemap URL
osm_tiles = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m)

ESRI_tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png'
folium.TileLayer(ESRI_tiles, attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community').add_to(m)
# add control to switch between baselayers
control = folium.LayerControl(collapsed=False)
map = st_folium(
    m,
    width=600, height=400,
    key="folium_map",
    layer_control=control
)

container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(r"""
    **The map shows the following:**
    """)
