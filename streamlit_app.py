import altair as alt
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import folium_static
import folium
from streamlit_folium import st_folium
from modules.nav import Navbar
# set icon for tabs in internet browsers
# setup page config
st.set_page_config(page_title="Pilot demonstrator", page_icon="🌍")
# setup page config using modules
Navbar()
# url PD2
url_pd2 = 'https://pilotdemonstrator2regionalbiodiversity.streamlit.app/'
st.sidebar.success("Select a tab above to choose the AOI for PD1")

st.title("Copernicus High-Cadence Monitoring for the EU Green Deal")
st.header("Welcome to the webapp landing page showcasing the pilot demonstrators")
st.write("Webapps are additional visualization for the reports written for the project")

st.image("data/logos/logos_companies.png", width=600, caption=["Companies in the consortium executing DEFIS/2022/OP/0012"])
container = st.container(border=True)
container.write(f"**Pilot demonstrator navigation**")
container.write("Use the tabs in the sidebar to explore pilot demonstrator 1 Common Agricultural Policy (CAP) subsidy monitoring")
container.write(f"Use the [link]({url_pd2}) to explore pilot demonstrator 2 Regional biodiversity monitoring")
container.write(f"Please note that this demonstrator is information dense and currently hosted on a community cloud. Therefore loading the data can take some time. For the best experience ensure a good internet connection and use a wide screen.")
st.write(
    """
    Click on the AOIs in the map to get a small description.
    Use the sidebar to view different visualizations developed for the AOI
    """
)




# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data

def load_geojson():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file('data/vectors/LPIS_Grasslands.geojson')
    # Convert the GeoDataFrame to a DataFrame
    df = pd.DataFrame(gdf)
    return df

def load_AOIs_geojsons():
    # Read GeoJSON data into a GeoDataFrame
    gdf1 = gpd.read_file("data/vectors/AOI_Betuwe.geojson")
    gdf2 = gpd.read_file("data/vectors/AOI_NOP.geojson")
    gdf3 = gpd.read_file("data/vectors/AOI_FrieseWouden.geojson")
    gdf4 = gpd.read_file("data/vectors/AOI_StBrieuc.geojson")
    # concat
    
    # Convert the GeoDataFrame to a DataFrame
    #df = pd.DataFrame(gdf)
    return gdf1,gdf2,gdf3,gdf4

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

def get_AOI_to_describe(tooltip_info):
    """
    very hacky but could not find any normal way to get info from tooltip
    """
    betuwe_description = f"""
    The Betuwe is an area in the center of the Netherlands between two major Dutch rivers; the Meuse and the Rhine. 
    It is a floodprone area with river deposited soils including heavy clay.
    In agricultural terms it is a widely known fruit producing area and has many grassland areas used predominantly for dairy cows.
    This AOI is selected to demonstrate regulation related to grassland management like **mowing** and **buffer strips** within the CAP.
    """

    nop_description = f"""The Noordoostpolder (NOP) is an area of reclaimed land from the in-land see 'Zuiderzee' (currently lake 'IJsselmeer') taken in use around 1942. 
    The soil is very fertile and it is a major agricultural area for field produce including large fields of tulips, wheat, carrot, potatoes.
    This AOI is selected to demonstrate regulation related to management like **ploughing** and **undersowing** within the CAP.
    """

    fw_description = f"""
    The Friese Wouden is a part in eastern Friesland at the border with province Groningen with agriculture predominantly focused on grasslands and maize for (dairy) cattle.
    Historically the area had many woodlands and wooded banks, tree lines are used for parcel delineation. 
    Furthermore this areas holds also many natural ponds created by collapsing ice lumps (so-called Pingo ruines) during melting after the ice-age and also has many water draining ditches. 
    This AOI is selected to demonstrate **High Diversity Landscape Features** within the CAP since the area is packed with both the 'green' and 'blue' landscape features.
    """
    stbr_description = f"""
    The Bay of Saint-Brieuc is located in Brittany, France. The region faces significant environmental challenges due to intensive agriculture and livestock farming, which lead to excessive nitrogen emissions. These emissions negatively impact wetlands, Natura2000 protected areas, and coastal ecosystems, causing issues like large algae blooms.
    This AOI is selected for Pilotdemonstrator 2 and is deployed on [a seperate website]({url_pd2}). Pilotdemonstrator 2 visualizes Earth Observation (EO) technology to monitor the effects of intensive farming on these ecosystems and assess the effectiveness of current Copernicus Land Monitoring Services (CLMS) and new EO sensors in supporting biodiversity and ecosystem protection.
    """

    AOI = str(tooltip_info).split('AOI')[1]
    if 'Betuwe' in AOI:
        return betuwe_description
    elif 'Noord Oost Polder (NOP)' in AOI:
        return nop_description
    elif 'Friese Wouden' in AOI:
        return fw_description
    elif 'Saint-Brieuc' in AOI:
        return stbr_description
    else: return AOI

betuwe,nop,fw,stbr = load_AOIs_geojsons()

# Create a map with the GeoJSON data using folium
m = folium.Map(location=[sum(nop.total_bounds[[1, 3]]) / 2, sum(nop.total_bounds[[0, 2]]) / 2], zoom_start=5)


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

folium.GeoJson(data=stbr,
                        name = 'Saint-Brieuc',
                        style_function=style_function_fw,
                        tooltip = folium.GeoJsonTooltip(fields=['AOI'])
            ).add_to(m)

map = st_folium(
    m,
    width=900, height=600,
    key="folium_map"
)
# use on click to describe AOI

if map.get("last_object_clicked_tooltip"):
    container = st.container(border=True)
    container.write(f"**AOI description**")
    container.write(get_AOI_to_describe(map["last_object_clicked_tooltip"]))
