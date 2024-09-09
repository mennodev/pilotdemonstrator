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
    gdf = gpd.read_file("data/vectors/Fields_AOI_FW_WGS84_brp2023c_LE.geojson")
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

def load_geojson_SWF():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/SWF_AOI_SUBSET_FW_WGS84_small.geojson")
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
container.write(f"**Definition of agricultural landscape features**")
container.markdown(f"""Landscape features are small fragments of 
non-productive natural or semi-natural vegetation in agricultural landscape which provide 
ecosystem services and support for biodiversity ([source: Technical Report JRC]({url_benefits_lf}))
""")
container.write(f"**Benefits of agricultural landscape features**")
container.markdown(f"""
    Agricultural benefits
    - Providing wood
    - Shelter for livestock
    - Barriers and demarcation between agricultural parcels
    - Windbreaks for crops
    - Increase productivity on steep slopes
    Societal benefits
    - Improved air quality
    - Improved water quality
    - Water quantity
    - Reduction of greenhouse gas emissions
    - Carbon sequestration
    - Climate change adaptation
    - Regulation of soil erosion and soil quality
    - Support biodiversity and pollination
    """)



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
df_LE_ammounts = df_LE_ammounts.set_index(df_LE_ammounts.columns[0])

st.write(f"**Types of agricultural landscape features**")
st.markdown(f"""
        **Agricultural landscape features in the context of EU are:**
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
st.write(f"**Types and occurence frequency of agricultural landscape features in the AOI**")
st.table(df_LE_ammounts)
st.write("From the table it is clear that water carying ditches are dominant. Also within the AOI almost all types of LF possible within the Dutch CAP are present apart from windhedge in orchards, earthen walls and terraces with shrubs. The latter only exists in province Limburg at some sloping terrains.")

st.subheader("CLMS HR SWF layer assessment")
st.write("To assess the usefullness of the CLMS High Resolution Small Woody Features layer regarding CAP regulation a very small subset is shown in the map below")
SWF_geojson = load_geojson_SWF()
geojson_FW = load_geojson_FW()

m_swf = folium.Map(location=[sum(SWF_geojson.total_bounds[[1, 3]]) / 2, sum(SWF_geojson.total_bounds[[0, 2]]) / 2], zoom_start=15)

# add ortho aerial imagery
folium.raster_layers.WmsTileLayer(url=r'https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
                layers = '2018_ortho25',
                transparent = True, 
                control = True,
                fmt="image/jpeg",
                name = 'Aerial Image 2018 RGB',
                attr = 'PDOK / opendata.beeldmaterial.nl',
                overlay = True,
                show = True,
                #CRS = 'EPSG:4326',
                ).add_to(m_swf)
# add geojson and add some styling
# add geojson and add some styling
folium.GeoJson(data=geojson_FW,
                        name = 'AOI Friese Wouden',
                        style_function=style_function_AOI,
                        #tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m_swf)

folium.GeoJson(data=SWF_geojson,
                        name = 'HR SWF',
                        style_function=style_function_AOI,
                        #tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m_swf)
control = folium.LayerControl(collapsed=False)
map = st_folium(
    m_swf,
    width=700, height=500,
    key="folium_map",
    layer_control=control
)

container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(r"""
    **The map shows the following:**
    - In general the area covered by the woody feature is overestimated
    - The polygons are not straight probably since it is derived from a 5 meter raster with jagged edges
    - Some tree lines seem to be ommitted
    
    **For CAP Landscape Features monitoring it means the following:**
    - Layer is usefull to get an overall indication of SWF density in a country
    - There is no distinction between SWF along or inside agricultural parcels and outside agricultural areas
    - Resolution is not sufficient for delineation checks or correct area estimates
    - Categorically it does not provide sufficient information to distinguish between different types of features
    - Cadence and delay in production is not sufficient for yearly monitoring
    """)

st.subheader("Assessment of Landscape Features declared in the LPIS")
st.write("To get an overview of landscape features a subset of the AOI is shown in the map below")
LE_geojson = load_geojson_LE()
geojson_FW = load_geojson_FW()

m = folium.Map(location=[sum(LE_geojson.total_bounds[[1, 3]]) / 2, sum(LE_geojson.total_bounds[[0, 2]]) / 2], zoom_start=10)

# add ortho aerial imagery
folium.raster_layers.WmsTileLayer(url=r'https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
                layers = '2023_ortho25',
                transparent = True, 
                control = True,
                fmt="image/jpeg",
                name = 'Aerial Image 2023 RGB',
                attr = 'PDOK / opendata.beeldmaterial.nl',
                overlay = True,
                show = True,
                #CRS = 'EPSG:4326',
                ).add_to(m)

#ESRI_tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png'
#folium.TileLayer(ESRI_tiles, attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',name='ESRI World Imagery').add_to(m)
# add control to switch between baselayers
# add geojson and add some styling
# add geojson and add some styling
folium.GeoJson(data=geojson_FW,
                        name = 'AOI Friese Wouden',
                        style_function=style_function_AOI,
                        #tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)

folium.GeoJson(data=LE_geojson,
                        name = 'Landscape Features in FW',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)
control = folium.LayerControl(collapsed=False)
map = st_folium(
    m,
    width=700, height=500,
    key="folium_map",
    layer_control=control
)

container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(r"""
    **The map shows the following:**
    - Not all landscape features are (yet) declared / delineated in 2023
    - Some ponds are cross-cut along parcel boundaries and do not form natural boundaries
    - Some mistakes can be identified e.g. row of trees overlapping ditches or overextending wooded banks
    """)
url_ahn = 'https://ahn.arcgisonline.nl/ahnviewer/'
st.subheader("Assessment of added values of altimetry data for Landscape Features monitoring")
st.write("In the Netherlands elevation data (AHN4) with 5 cm horizontal and 50cm vertical resolution is freely available ([see also this viewer]({url_ahn})). To get an overview of how altimetry can be used a Digital Surface Model is displayed in the map below")
#LE_geojson = load_geojson_LE()
#geojson_FW = load_geojson_FW()

m_ahn = folium.Map(location=[sum(LE_geojson.total_bounds[[1, 3]]) / 2, sum(LE_geojson.total_bounds[[0, 2]]) / 2], zoom_start=12)
# add ortho aerial imagery
folium.raster_layers.WmsTileLayer(url=r'https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
                layers = '2020_ortho25',
                transparent = True, 
                control = True,
                fmt="image/jpeg",
                name = 'Aerial Image 2020 RGB',
                attr = 'PDOK / opendata.beeldmaterial.nl',
                overlay = True,
                show = True,
                #CRS = 'EPSG:4326',
                ).add_to(m_ahn)
# add ortho aerial imagery
folium.raster_layers.WmsTileLayer(url=r'https://service.pdok.nl/rws/ahn/wms/v1_0',
                layers = 'dsm_05m',
                transparent = True, 
                control = True,
                fmt="image/png",
                name = 'DSM AHN4 2020',
                attr = 'PDOK / opendata.beeldmaterial.nl',
                overlay = True,
                show = True,
                #CRS = 'EPSG:4326',
                ).add_to(m_ahn)

#ESRI_tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png'
#folium.TileLayer(ESRI_tiles, attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',name='ESRI World Imagery').add_to(m)
# add control to switch between baselayers
# add geojson and add some styling
# add geojson and add some styling
folium.GeoJson(data=geojson_FW,
                        name = 'AOI Friese Wouden',
                        style_function=style_function_AOI,
                        #tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m_ahn)

folium.GeoJson(data=LE_geojson,
                        name = 'Landscape Features in FW',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m_ahn)
control = folium.LayerControl(collapsed=False)
map = st_folium(
    m_ahn,
    width=700, height=500,
    key="folium_map",
    layer_control=control
)

container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(r"""
    **The map shows the following:**
    - The DSM is very suitable to discriminate between landscape features and surrounding fields
    - Ponds and some water carrying ditch  are clearly distinguisable as NoData
    - Many landscape features are not declared in the LPIS
    - LPIS declarations are often clearly visible in the DSM of 2020 meaning that not many mutation happen in the landscape
    - Cadence of the DSM would ideally increase to at least yearly to match CAP regulation
    """)
url_bag = 'https://bagviewer.kadaster.nl/lvbag/bag-viewer/?theme=BRT+Achtergrond&geometry.x=211126.63057978588&geometry.y=575577.8156218333&zoomlevel=12.028149392472756'
st.write('In order to make the altimetry data more useful for automated landscape feature analysis the data can be segmented into a binary layer with high objects and low objects. Further the open-source layer BAG (Administration of Buildings and Adresses) can be leveraged to filter out all buildings. ([see for example of buildings in the AOI this viewer]({url_bag})). This results in a vector layer which can be used in geometric analysis for example by querying whether the declared LPIS is overlapping a feature classified as a high object without being a building')
st.image("data/images/SegmentedAHN.png", width=700, caption=["Creating a categorical vector layer from the DSM representing all high objects in the landscape for automated landscape feature analysis"])
st.write('Such layers or the LPIS itself can be enriched with statistics from the altimetry. For example the average height of the polygon can be represented. With a scrub hedge lower heights are being to be expected compared to a tree-lined avenue. Also a timeserie of optical data can be processed to determine a shadow score. Using the sun and satellite angle and a stack of optical data all polygons are given a shadow score. Meaning that if all pixels in the vector can be associated with an expected shadow the score is high and low if no shadows can be found. This number is associated with the feature being sparse and not generating much shadow')
st.image("data/images/WeighedAHNvectors.png", width=700, caption=["Enriching vector layers with average height (left) or a shadow score (right) with purple values being low values and green/yellow high values"])
st.write("An additional technology to get categorical data on landscape features is to deploy machine learning techniques like object detection to distinguish between different types of landscape features. Within an innovation trajectory by the paying agency in 2020 two companies from the Netherlands (TerraSphere and Arcadis) showed that using VHR optical data and aerial imagery could reliably detect landscape features on scale (1.1 milion elements in 3 Dutch provinces).")
st.image("data/images/DeepLearningResult.png", width=700, caption=["Vector layer displaying the result of deep learning object segementation using aerial imagery"])
container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(r"""
    **The displayed images shows the following:**
    - Additioanl techniques can be leveraged to aid in landscape feature detection like using altimetry, shadow and altimetry
    - Continuity of presence and type of landscape feature can be determined
    **Overal conclusion:**
    - Management like pruning woody features, trimming hedges and removal of exotic species within the feature are hardly visible with spaceborne and aerial EO
    - Side looking images and reporting during management is key. Mobile applications like RVO GeoTAG are probably the best monitoring tool for landscape feature management 
    - SLI can aid in generating large ins-itu datasets for algorithm training for automated landscape feature detection
    - Deep learning algorithms can help paying agencies to automate checks in landscape feature monitoring
    """)