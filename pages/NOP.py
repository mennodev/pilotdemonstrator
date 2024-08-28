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
# Header
# Navbar()

st.title("Pilot demonstrator AOI Noord Oost Polder")

st.header("Demonstrator focusing on soil cover regulations in the CAP and relation to cadency")
st.write(
    """
    Below you find different blocks of data visualization developed in the pilot demonstrator exploring the topic in AOI NOP. 
    """
)

# Helper functions

# Translation dictionary
translation_dict = {
    'Aardappelen, bestrijdingsmaatregel AM':'Potatoes, control measure AM',
    'Aardappelen, consumptie':'Potatoes, consumption',
    'Aardappelen, poot NAK':'Potatoes, planting NAK',
    'Aardappelen, poot TBM':'Potatoes, planting TBM',
    'Aardappelen, zetmeel':'Potatoes, starch',
    'Aardbeien op stellingen, productie':'Strawberries on racks, production',
    'Aardbeien open grond, productie':'Strawberries open ground, production',
    'Aardbeien open grond, vermeerdering':'Strawberries open ground, propagation',
    'Aardbeien open grond, zaden en opkweekmateriaal':'Strawberries open ground, seeds and growing material',
    'Agrarisch natuurmengsel':'Agricultural natural mixture',
    'Amaryllis, bloembollen en -knollen':'Amaryllis, flower bulbs and tubers',
    'Appels. Aangeplant lopende seizoen.':'Apples. Planted current season.',
    'Appels. Aangeplant voorafgaande aan lopende seizoen.':'Apples. Planted prior to current season.',
    'Asperges, oppervlakte die nog geen productie oplevert':'Asparagus, area not yet producing',
    'Asperges, oppervlakte die productie oplevert':'Asparagus, area producing',
    'Bessen, blauwe':'Berries, blue',
    'Bieten, suiker-':'Beets, sugar-',
    'Bieten, voeder-':'Beets, fodder-',
    'Bladrammenas':'Leaf radish',
    'Blauw druifje, bloembollen en -knollen':'Blue grape hyacinth, flower bulbs and tubers',
    'Blauwmaanzaad':'Blue poppy seed',
    'Bloemkool, winter, productie':'Cauliflower, winter, production',
    'Bloemkool, zomer, productie':'Cauliflower, summer, production',
    'Bloemzaden open grond':'Flower seeds open ground',
    'Boerenkool, productie':'Kale, production',
    'Boerenkool, zaden en opkweekmateriaal':'Kale, seeds and growing material',
    'Bonen, bruine-':'Beans, brown-',
    'Bonen, tuin- (droog te oogsten) (geen consumptie)':'Beans, garden- (harvest dry) (not for consumption)',
    'Bonen, tuin- (groen te oogsten)':'Beans, garden- (harvest green)',
    'Bonen, veld- (onder andere duiven-, paarden-, wierbonen)':'Beans, field- (including pigeon-, horse-, seaweed beans)',
    'Boomgroep':'Tree group',
    'Bos- en haagplanten, open grond':'Forest and hedge plants, open ground',
    'Bos, blijvend, met herplantplicht':'Forest, permanent, with replanting obligation',
    'Bosje':'Bunch',
    'Bospeen, productie':'Carrot, production',
    'Bossingel':'Bossingel',
    'Bramen':'Blackberries',
    'Broccoli, productie':'Broccoli, production',
    'Buxus, open grond':'Buxus, open ground',
    'Chinese kool, productie':'Chinese cabbage, production',
    'Cichorei':'Chicory',
    'Dahlia, bloembollen en - knollen':'Dahlia, flower bulbs and - tubers',
    'Dahlia, droogbloemen':'Dahlia, dried flowers',
    'Dahlia, overige bloemkwekerijgewassen':'Dahlia, other flower nursery crops',
    'Drachtplanten':'Nectar plants',
    'Engels raaigras, graszaad':'English ryegrass, grass seed',
    'Engels raaigras, groenbemesting, vanggewas':'English ryegrass, green manure, catch crop',
    'Erwten (droog te oogsten)':'Peas (harvest dry)',
    'Erwten, groene/gele (groen te oogsten)':'Peas, green/yellow (harvest green)',
    'Facelia':'Facelia',
    'Gerst, winter-':'Barley, winter-',
    'Gerst, zomer-':'Barley, summer-',
    'Gladiool, bloembollen en - knollen':'Gladiolus, flower bulbs and tubers',
    'Goudsbloem':'Marigold',
    'Granen, overig':'Grains, other',
    'Grasland, blijvend':'Grassland, permanent',
    'Grasland, natuurlijk. Hoofdfunctie natuur.':'Grassland, natural. Main function nature.',
    'Grasland, natuurlijk. Met landbouwactiviteiten.':'Grassland, natural. With agricultural activities.',
    'Grasland, tijdelijk':'Grassland, temporary',
    'Groene braak, spontane opkomst':'Green fallow, spontaneous emergence',
    'Haver':'Oats',
    'Hennep, vezel-':'Hemp, fibre',
    'Hoogstamboomgaard':'High-stem orchard',
    'Houtwal en houtsingel':'Wooden bank and hedgerow',
    'Hyacint, bloembollen en - knollen':'Hyacinth, flower bulbs and tubers',
    'Iris, Bolvormend':'Iris, Bulb-forming',
    'Iris, Rhizoomvormend':'Iris, Rhizome-forming',
    'Italiaans raaigras, graszaad':'Italian ryegrass, grass seed',
    'Kersen, zoet':'Cherries, sweet',
    'Klaver, Alexandrijnse, groenbemesting, vanggewas':'Clover, Alexandrian, green manure, catch crop',
    'Klaver, rode, groenbemesting, vanggewas':'Clover, red, green manure, catch crop',
    'Klaver, witte, groenbemesting, vanggewas':'Clover, white, green manure, catch crop',
    'Knip- of scheerheg':'Cut or shear hedge',
    'Knoflook':'Garlic',
    'Knolselderij, productie':'Celeriac, production',
    'Koolraap, productie':'Tulip, production',
    'Koolzaad, winter (incl. boterzaad)':'Rapeseed, winter (incl. butterseed)',
    'Koolzaad, zomer (incl. boterzaad)':'Rapeseed, summer (incl. butterseed)',
    'Krokus, bloembollen en - knollen':'Crocus, flower bulbs and tubers',
    'Kroten/rode bieten, productie':'Beets/red beets, production',
    'Laanbomen/parkbomen, opzetters, open grond':'Avenue trees/park trees, erectors, open ground',
    'Laanbomen/parkbomen, opzetters, pot- en containerveld':'Avenue trees/park trees, erectors, pot and container field',
    'Laanbomen/parkbomen, spillen, open grond':'Avenue trees/park trees, spindles, open ground',
    'Landschapselement, overig':'Landscape element, other',
    'Leibomen':'Espalier trees',
    'Lelie, bloembollen en -knollen':'Lily, flower bulbs and tubers',
    'Lelie, overige bloemkwekerijgewassen':'Lily, other nursery crops',
    'Luzerne':'Alfalfa',
    'Mais, corncob mix':'Maize, corncob mix',
    'Mais, korrel-':'Maize, grain-',
    'Mais, snij-':'Maize, cut-',
    'Mais, suiker-':'Maize, sugar-',
    'Maiskolvensilage':'Corn cob silage',
    'Narcis, bloembollen en -knollen':'Daffodil, flower bulbs and tubers',
    'Natuurterreinen (incl. heide)':'Nature areas (incl. heathland)',
    'Natuurvriendelijke oever':'Nature-friendly bank',
    'Notenbomen':'Nut trees',
    'Onbeteelde grond vanwege een teeltverbod/ontheffing':'Uncultivated land due to a cultivation ban/exemption',
    'Overig graszaad':'Other grass seed',
    'Overig klaverzaad':'Other clover seed',
    r"Overig kleinfruit (zoals kruisbessen, kiwi's)":'Other soft fruit (such as gooseberries, kiwis)',
    'Overige akkerbouwgewassen':'Other arable crops',
    'Overige bloemen, bloembollen en -knollen':'Other flowers, flower bulbs and tubers',
    'Overige bloemen, overige bloemkwekerijgewassen':'Other flowers, other nursery crops',
    'Overige groenbemesters, niet-vlinderbloemige-':'Other green manures, non-leguminous-',
    'Overige groenbemesters, vlinderbloemige-':'Other green manures, leguminous-',
    'Overige niet genoemde bladgewassen, productie':'Other not mentioned leafy crops, production',
    'Overige niet genoemde groenten, productie':'Other not mentioned vegetables, production',
    'Overige niet genoemde groenten, zaden en opkweekmateriaal':'Other not mentioned vegetables, seeds and propagation material',
    'Pastinaak, productie':'Parsnip, production',
    'Peren. Aangeplant lopende seizoen.':'Pears. Planted current season.',
    'Peren. Aangeplant voorafgaande aan lopende seizoen.':'Pears. Planted prior to current season.',
    'Peterselie, zaden en opkweekmateriaal':'Parsley, seeds and propagation material',
    'Pioenroos, droogbloemen':'Peony, dried flowers',
    'Pioenroos, overige bloemkwekerijgewassen':'Peony, other flower nursery crops',
    'Pioenroos, vermeerdering':'Peony, propagation',
    'Poel en klein historisch water':'Pond and small historical water',
    'Pompoen, productie':'Pumpkin, production',
    'Pompoen, zaden en opkweekmateriaal':'Pumpkin, seeds and propagation material',
    'Prei, winter, productie':'Leek, winter, production',
    'Prei, zomer, productie':'Leek, summer, production',
    'Pruimen':'Plums',
    'Quinoa':'Quinoa',
    'Raapstelen, zaden en opkweekmateriaal':'Turnip tops, seeds and propagation material',
    'Rabarber, productie':'Rhubarb, production',
    'Radijs, zaden en opkweekmateriaal':'Radish, seeds and propagation material',
    'Raketblad (aaltjesvanggewas)':'Rocket leaf (nematode trap crop)',
    'Rand, liggend op bouwland en direct grenzend aan bos. Geen landbouwproductie.':'Edge, lying on arable land and directly bordering on forest. No agricultural production.',
    'Riet':'Reed',
    'Rietzoom en klein rietperceel':'Reed border and small reed plot',
    'Rodekool, productie':'Red cabbage, production',
    'Rogge (geen snijrogge)':'Rye (not cut rye)',
    'Ruigtes op landbouwpercelen':'Roughs on agricultural plots',
    'Savooiekool, productie':'Savoy cabbage, production',
    'Schorseneren, zaden en opkweekmateriaal':'Scorzonera, seeds and growing material',
    'Schouwpad':'Inspection path',
    'Sierconiferen, pot- en containerveld':'Ornamental conifers, pot and container field',
    'Sierheesters en klimplanten, pot- en containerveld':'Ornamental shrubs and climbers, pot and container field',
    'Sierui, bloembollen en -knollen':'Ornamental onion, flower bulbs and tubers',
    'Sjalotten':'Shallots',
    'Sla, overig, productie':'Lettuce, other, production',
    'Sla, radicchio rosso, productie':'Lettuce, radicchio rosso, production',
    'Snijgroen':'Cut greens',
    'Sojabonen':'Soya beans',
    'Spelt':'Spelt',
    'Spinazie, productie':'Spinach, production',
    'Spinazie, zaden en opkweekmateriaal':'Spinach, seeds and growing material',
    'Spitskool, productie':'Pointed cabbage, production',
    'Spruitkool/spruitjes, productie':'Brussels sprouts, production',
    'Stamsperziebonen (=stamslabonen), productie':'Pollar green beans (=pollar French beans), production',
    'Stamsperziebonen (=stamslabonen), zaden en opkweekmateriaal':'Pollar green beans (=pollar French beans), seeds and growing material',
    'Stroken wild gras':'Strands of wild grass',
    'Struweelhaag':'Hedgerow',
    'Tagetes erecta (Afrikaantje)':'Tagetes erecta (Amarigold)',
    'Tagetes patula (Afrikaantje)':'Tagetes patula (Tagetes)',
    'Tarwe, winter-':'Wheat, winter-',
    'Tarwe, zomer-':'Wheat, summer-',
    'Triticale':'Triticale',
    'Tulp, bloembollen en -knollen':'Tulip, flower bulbs and tubers',
    'Tuunwallen':'Garden walls',
    'Uien, gele zaai-':'Onions, yellow sowing-',
    'Uien, poot en plant, 1e jaars':'Onions, plant and plant, 1st year',
    'Uien, poot en plant, 2e jaars':'Onions, plant and plant, 2nd year',
    'Uien, rode zaai-':'Onions, red sowing-',
    'Uien, zilver-':'Onions, silver-',
    'Vaste planten, open grond':'Perennials, open ground',
    'Vaste planten, pot- en containerteelt':'Perennials, pot and container cultivation',
    'Vlas, olie-. Lijnzaad niet van vezelvlas':'Flax, oil-. Linseed not from fibre flax',
    'Vlas, vezel-':'Flax, fibre-',
    'Voedselbos':'Food forest',
    'Vruchtbomen, moerbomen, open grond':'Fruit trees, nut trees, open ground',
    'Vruchtbomen, onderstammen, open grond':'Fruit trees, rootstocks, open ground',
    'Vruchtbomen, overig, open grond':'Fruit trees, other, open ground',
    'Waspeen, productie':'Carrots, production',
    'Water, overig':'Water, other',
    'Wijndruiven':'Wine grapes',
    'Windhaag, in een perceel fruitteelt':'Windbreak hedge, in a fruit growing plot',
    'Winterpeen, productie':'Winter carrots, production',
    'Witlofwortel, productie':'Chicory root, production',
    'Witlofwortel, zaden en opkweekmateriaal':'Chicory root, seeds and growing material',
    'Witte kool, productie':'White cabbage, production',
    'Wortelpeterselie':'Root parsley',
    'Zoete aardappelen':'Sweet potatoes',
}

color_dict ={
    'Aardappelen, bestrijdingsmaatregel AM':'blue',
    'Aardappelen, consumptie':'blue',
    'Aardappelen, poot NAK':'blue',
    'Aardappelen, poot TBM':'blue',
    'Aardappelen, zetmeel':'blue',
    'Aardbeien op stellingen, productie':'green',
    'Aardbeien open grond, productie':'green',
    'Aardbeien open grond, vermeerdering':'green',
    'Aardbeien open grond, zaden en opkweekmateriaal':'green',
    'Agrarisch natuurmengsel':'green',
    'Amaryllis, bloembollen en -knollen':'pink',
    'Appels. Aangeplant lopende seizoen.':'green',
    'Appels. Aangeplant voorafgaande aan lopende seizoen.':'green',
    'Asperges, oppervlakte die nog geen productie oplevert':'green',
    'Asperges, oppervlakte die productie oplevert':'green',
    'Bessen, blauwe':'green',
    'Bieten, suiker-':'green',
    'Bieten, voeder-':'green',
    'Bladrammenas':'green',
    'Blauw druifje, bloembollen en -knollen':'pink',
    'Blauwmaanzaad':'green',
    'Bloemkool, winter, productie':'green',
    'Bloemkool, zomer, productie':'green',
    'Bloemzaden open grond':'pink',
    'Boerenkool, productie':'green',
    'Boerenkool, zaden en opkweekmateriaal':'green',
    'Bonen, bruine-':'green',
    'Bonen, tuin- (droog te oogsten) (geen consumptie)':'green',
    'Bonen, tuin- (groen te oogsten)':'green',
    'Bonen, veld- (onder andere duiven-, paarden-, wierbonen)':'green',
    'Boomgroep':'green',
    'Bos- en haagplanten, open grond':'green',
    'Bos, blijvend, met herplantplicht':'green',
    'Bosje':'green',
    'Bospeen, productie':'orange',
    'Bossingel':'green',
    'Bramen':'green',
    'Broccoli, productie':'green',
    'Buxus, open grond':'green',
    'Chinese kool, productie':'green',
    'Cichorei':'green',
    'Dahlia, bloembollen en - knollen':'pink',
    'Dahlia, droogbloemen':'pink',
    'Dahlia, overige bloemkwekerijgewassen':'pink',
    'Drachtplanten':'pink',
    'Engels raaigras, graszaad':'lightgreen',
    'Engels raaigras, groenbemesting, vanggewas':'lightgreen',
    'Erwten (droog te oogsten)':'green',
    'Erwten, groene/gele (groen te oogsten)':'green',
    'Facelia':'green',
    'Gerst, winter-':'yellow',
    'Gerst, zomer-':'yellow',
    'Gladiool, bloembollen en - knollen':'pink',
    'Goudsbloem':'pink',
    'Granen, overig':'yellow',
    'Grasland, blijvend':'lightgreen',
    'Grasland, natuurlijk. Hoofdfunctie natuur.':'lightgreen',
    'Grasland, natuurlijk. Met landbouwactiviteiten.':'lightgreen',
    'Grasland, tijdelijk':'lightgreen',
    'Groene braak, spontane opkomst':'green',
    'Haver':'yellow',
    'Hennep, vezel-':'green',
    'Hoogstamboomgaard':'green',
    'Houtwal en houtsingel':'green',
    'Hyacint, bloembollen en - knollen':'pink',
    'Iris, Bolvormend':'pink',
    'Iris, Rhizoomvormend':'pink',
    'Italiaans raaigras, graszaad':'lightgreen',
    'Kersen, zoet':'green',
    'Klaver, Alexandrijnse, groenbemesting, vanggewas':'magenta',
    'Klaver, rode, groenbemesting, vanggewas':'magenta',
    'Klaver, witte, groenbemesting, vanggewas':'magenta',
    'Knip- of scheerheg':'green',
    'Knoflook':'green',
    'Knolselderij, productie':'green',
    'Koolraap, productie':'green',
    'Koolzaad, winter (incl. boterzaad)':'green',
    'Koolzaad, zomer (incl. boterzaad)':'green',
    'Krokus, bloembollen en - knollen':'pink',
    'Kroten/rode bieten, productie':'green',
    'Laanbomen/parkbomen, opzetters, open grond':'green',
    'Laanbomen/parkbomen, opzetters, pot- en containerveld':'green',
    'Laanbomen/parkbomen, spillen, open grond':'green',
    'Landschapselement, overig':'green',
    'Leibomen':'green',
    'Lelie, bloembollen en -knollen':'pink',
    'Lelie, overige bloemkwekerijgewassen':'pink',
    'Luzerne':'green',
    'Mais, corncob mix':'yellow',
    'Mais, korrel-':'yellow',
    'Mais, snij-':'yellow',
    'Mais, suiker-':'yellow',
    'Maiskolvensilage':'yellow',
    'Narcis, bloembollen en -knollen':'pink',
    'Natuurterreinen (incl. heide)':'green',
    'Natuurvriendelijke oever':'green',
    'Notenbomen':'green',
    'Onbeteelde grond vanwege een teeltverbod/ontheffing':'green',
    'Overig graszaad':'lightgreen',
    'Overig klaverzaad':'green',
    r"Overig kleinfruit (zoals kruisbessen, kiwi's)":'green',
    'Overige akkerbouwgewassen':'green',
    'Overige bloemen, bloembollen en -knollen':'pink',
    'Overige bloemen, overige bloemkwekerijgewassen':'pink',
    'Overige groenbemesters, niet-vlinderbloemige-':'magenta',
    'Overige groenbemesters, vlinderbloemige-':'magenta',
    'Overige niet genoemde bladgewassen, productie':'green',
    'Overige niet genoemde groenten, productie':'green',
    'Overige niet genoemde groenten, zaden en opkweekmateriaal':'green',
    'Pastinaak, productie':'green',
    'Peren. Aangeplant lopende seizoen.':'green',
    'Peren. Aangeplant voorafgaande aan lopende seizoen.':'green',
    'Peterselie, zaden en opkweekmateriaal':'green',
    'Pioenroos, droogbloemen':'pink',
    'Pioenroos, overige bloemkwekerijgewassen':'pink',
    'Pioenroos, vermeerdering':'pink',
    'Poel en klein historisch water':'lightblue',
    'Pompoen, productie':'green',
    'Pompoen, zaden en opkweekmateriaal':'green',
    'Prei, winter, productie':'green',
    'Prei, zomer, productie':'green',
    'Pruimen':'green',
    'Quinoa':'green',
    'Raapstelen, zaden en opkweekmateriaal':'green',
    'Rabarber, productie':'green',
    'Radijs, zaden en opkweekmateriaal':'green',
    'Raketblad (aaltjesvanggewas)':'green',
    'Rand, liggend op bouwland en direct grenzend aan bos. Geen landbouwproductie.':'green',
    'Riet':'green',
    'Rietzoom en klein rietperceel':'green',
    'Rodekool, productie':'green',
    'Rogge (geen snijrogge)':'yellow',
    'Ruigtes op landbouwpercelen':'green',
    'Savooiekool, productie':'green',
    'Schorseneren, zaden en opkweekmateriaal':'green',
    'Schouwpad':'green',
    'Sierconiferen, pot- en containerveld':'pink',
    'Sierheesters en klimplanten, pot- en containerveld':'pink',
    'Sierui, bloembollen en -knollen':'pink',
    'Sjalotten':'purple',
    'Sla, overig, productie':'green',
    'Sla, radicchio rosso, productie':'green',
    'Snijgroen':'green',
    'Sojabonen':'green',
    'Spelt':'yellow',
    'Spinazie, productie':'green',
    'Spinazie, zaden en opkweekmateriaal':'green',
    'Spitskool, productie':'green',
    'Spruitkool/spruitjes, productie':'green',
    'Stamsperziebonen (=stamslabonen), productie':'green',
    'Stamsperziebonen (=stamslabonen), zaden en opkweekmateriaal':'green',
    'Stookroos, open grond':'pink',
    'Stookroos, pot- en containerveld':'pink',
    'Struikheide':'green',
    'Suikermais, productie':'yellow',
    'Suikermais, zaden en opkweekmateriaal':'yellow',
    'Tamme kastanjes':'green',
    'Tarwe, winter-':'yellow',
    'Tarwe, zomer-':'yellow',
    'Troschrysant, open grond':'pink',
    'Tulpen, bloembollen en -knollen':'pink',
    'Ui, geel':'purple',
    'Ui, rood':'purple',
    'Uitgeschoten grasland':'lightgreen',
    'Valeriaan, productie':'green',
    'Valeriaan, zaden en opkweekmateriaal':'green',
    'Veldsla, zaden en opkweekmateriaal':'green',
    'Vijgen':'green',
    'Voedselbos':'green',
    'Voederbieten':'green',
    'Voederboon':'green',
    'Witte kool, productie':'green',
    'Zonnebloemen':'pink',
    'Zomereik':'green',
    'Zomergerst, productie':'yellow',
    'Zomertarwe, productie':'yellow',
    'Zomerwikke, groenbemesting, vanggewas':'green',
    'Zomerwortelen, productie':'orange'
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

def load_seasondate_ppi():
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
    #df['management'] = df['gws_gewas'].map(translation_dict)
    df['color'] = df['gws_gewas'].map(color_dict)
    return df

def load_geojson_LPIS():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/Fields_AOI_NOP_WGS84_brp2023c_subset.geojson")
    # translate to English
    gdf['management'] = gdf['gws_gewas'].map(translation_dict)
    gdf['color'] = gdf['gws_gewas'].map(color_dict)
    # Convert the GeoDataFrame to a DataFrame
    #df = pd.DataFrame(gdf)
    return gdf

def load_geojson_NOP():
    # Read GeoJSON data into a GeoDataFrame
    gdf = gpd.read_file("data/vectors/AOI_NOP.geojson")
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





# Add the Folium map to the Streamlit app using the st_folium library
url_benefits_soilcover = 'https://web.archive.org/web/20210815035434/http://agro.icm.edu.pl/agro/element/bwmeta1.element.agro-f380246b-6231-47a0-86ac-90495cfcd7af/c/Catch_crops_and_the_soil_environment__a_review_of_the_literature.pdf'
st.subheader("Soil cover in the NOP")
st.markdown(f"""Covering soil with biomass is important since it provides several services to increase soil capabilities and in turn aid biodiversity and agricultural production ([see also this paper]({url_benefits_soilcover}))
            - Protects the soil against erosion. In the AOI surface water run-off is not relevant, but wind erosion is.
            - Protects the soil against direct sunlight benefitting soil life and moisture retention
            - Prevents compaction or sealing of the soil, thereby allowing next crops to better root and aiding in moisture retention.
            - Better circumstance (e.g. by adding humic substances) to sustain different types of soil life, root interaction with micro-organisms etc. 
            - Agricultural production is increased by providing more water availability, healthy airy soils and more nutrients for the produce. 
            - Legumes as a green manure provide additional nutrients sequestered from the air and stored in the soil. 
            - Catch crops prevent migration of nutrients (mainly N and P) to deeper soil layers 
""")
# When the user interacts with the map
# Create a map with the GeoJSON data using folium
st.write(f"""LPIS data of 2023 for the AOI reveals that 88% of parcels are croplands, with the remaining part predominantly covered with grasslands (11,2%).
            The subset below also shows that dominant crops are potatoes (blue polygons) and cereals (yellow polygons)""")
geojson_LPIS = load_geojson_LPIS()
geojson_NOP = load_geojson_NOP()
m = folium.Map(location=[sum(geojson_NOP.total_bounds[[1, 3]]) / 2, sum(geojson_NOP.total_bounds[[0, 2]]) / 2], zoom_start=11)
# add geojson and add some styling
folium.GeoJson(data=geojson_LPIS,
                        name = 'Subset of LPIS NOP',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)
# add geojson and add some styling
folium.GeoJson(data=geojson_NOP,
                        name = 'AOI NOP',
                        #style_function=style_function,
                        #tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)


# Set the basemap URL
osm_tiles = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m)
map = st_folium(
    m,
    width=500, height=500,
    key="folium_map"
)
with st.expander("Toggle linked Sentinel-2 plot",expanded=True):
    df = load_seasondate_ppi()

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
