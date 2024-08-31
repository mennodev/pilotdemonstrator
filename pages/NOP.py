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

# display navbar for switching to other topics
Navbar()

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
    110: 'D110',
    15: 'A015',
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
    df = pd.read_csv("data/dataframes/seasondates_parcels_NOP.csv")
    # subselect columns and rename for plotting
    df = df[["gid","EOSD_T31UFU_s2","SOSD_T31UFU_s2","EOSD_T31UFU_s1","SOSD_T31UFU_s1"]]

    df = df.rename(columns={"EOSD_T31UFU_s2":"EOS date season 2",
                            "SOSD_T31UFU_s2":"SOS date season 2",
                            "SOSD_T31UFU_s1":"SOS date season 1",
                            "EOSD_T31UFU_s1":"EOS date season 1" })
      
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

def load_ndvi_nop():
    # parquet file
    df = pd.read_parquet("data/dataframes/NDVI_AOI_NOP_BRP2023c.parquet", engine='pyarrow')
    return df

def load_bsi_nop():
    # parquet file
    df = pd.read_parquet("data/dataframes/BSI_AOI_NOP_BRP2023c.parquet", engine='pyarrow')
    return df

def load_bsi12_nop():
    # parquet file
    df = pd.read_parquet("data/dataframes/BSI12_AOI_NOP_BRP2023c.parquet", engine='pyarrow')
    return df

def load_nbr_nop():
    # parquet file
    df = pd.read_parquet("data/dataframes/NBR_AOI_NOP_BRP2023c.parquet", engine='pyarrow')
    return df

def load_s2wi_nop():
    # parquet file
    df = pd.read_parquet("data/dataframes/S2WI_AOI_NOP_BRP2023c.parquet", engine='pyarrow')
    return df

def load_GRD_parquet():
    df = pd.read_parquet("data/dataframes/GRD_VV_VH_parcels_NOP.parquet", engine='pyarrow')
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
    df = pd.read_csv("data/dataframes/coh_parcels_NOP.csv")
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
    return {"color":x['properties']['color'], "weight":1}

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

def style_function_AOI(x):
    """
    Use color column to assign color
    """
    return {"color":'blue', "weight":1, "fillOpacity":0.0}

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
container = st.container(border=True)

container.write(f"**General benefits of soil cover**")
container.markdown(f"""
            Covering soil with biomass is important since it provides several services to increase soil capabilities and in turn aid biodiversity and agricultural production ([see also this paper]({url_benefits_soilcover}))
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
            The subset of LPIS data below also shows that dominant crops in the AOI are potatoes (blue polygons) and cereals (yellow polygons)
            """)

geojson_LPIS = load_geojson_LPIS()
geojson_NOP = load_geojson_NOP()
m = folium.Map(location=[sum(geojson_NOP.total_bounds[[1, 3]]) / 2, sum(geojson_NOP.total_bounds[[0, 2]]) / 2], zoom_start=11)
# add geojson and add some styling

# add geojson and add some styling
folium.GeoJson(data=geojson_NOP,
                        name = 'AOI NOP',
                        style_function=style_function_AOI,
                        #tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)

folium.GeoJson(data=geojson_LPIS,
                        name = 'Subset of LPIS NOP',
                        style_function=style_function,
                        tooltip = folium.GeoJsonTooltip(fields=['gid','management','gewascode'])
                        ).add_to(m)
# Set the basemap URL
osm_tiles = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
folium.TileLayer(osm_tiles, attr='Map data © OpenStreetMap contributors').add_to(m)
map = st_folium(
    m,
    width=700, height=400,
    key="folium_map"
)
df_season_doy = load_seasondate_ppi()
df_ndvi = load_ndvi_nop()
with st.expander("Toggle linked NDVI and phenological DOY plot",expanded=True):
    
    gid_to_plot = 1400841
    if map.get("last_object_clicked_tooltip"):
        gid_to_plot = get_gid_from_tooltip(map["last_object_clicked_tooltip"])
    if gid_to_plot is not None:
        # subselect data
        df_selection = df_ndvi.loc[df_ndvi['gid'] == gid_to_plot]
        df_season_doy_selected = df_season_doy.loc[df_season_doy['gid'] == gid_to_plot]
        # Display line chart
        chart = alt.Chart(df_selection).mark_line(point={
        "filled": False,
        "fill": "white"
        }).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('NDVI:Q', title='NDVI'),
                    #color='genre:N'
                    ).properties(height=320)
        st.write(f'Chart of NDVI reads by Sentinel-2 and phenological information from CLMS HR-VPP for selected field {gid_to_plot}')
    
            # add mowing and grazing dates if df is not empty
        if not df_season_doy_selected.empty:
            # melt so it is suitable for altair
            df_long = df_season_doy_selected.melt(id_vars=['gid'], value_vars=["EOS date season 2","SOS date season 2","SOS date season 1","EOS date season 1"],
                  var_name='date of season variable', value_name='date')
            doy_plot = alt.Chart(df_long).mark_rule().encode(
                x='date:T',
                color=alt.Color('date of season variable'),
                #strokeDash=alt.StrokeDash('event:N', title='Event Type'),  # Dash by event type
                size=alt.value(2),  # Set line width
            )
            # update final chart
            chart += doy_plot

        st.altair_chart(chart.interactive(), use_container_width=True)

container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(
    """
    **The products from the CLMS HRVPP like the layers indicating Start of Season and End of Season dates are very useful**
    - **It directly shows whether there is 1 or 2 crops in a season, the length of the season, timing of the on-set and the harvest of the crop**
    - **This information can be directly linked to the declared crop and whether the season characteristics are logical**
    - **Plotting biomass reads along the layer information confirms in most cases the given seasonal characteristics**
        + For example winter wheats have a much earlier onset compared to potatoes
        + Method is applied indiscriminately e.g. grasslands are also given a EOS and SOS
    - **Only HR VPP information is not sufficient to answer all question on soil cover since it only provided information for distinguished seasons**
    - **Soil cover analysis requires biomass information of fields also outside the production season**
    """)
st.write(f"""For sensors with capabilities to measure blue, read, near infrared (NIR) and short wave infrared (SWIR) spectral bands the Bare Soil Index (BSI) can be calculated. The rationale behind this index is that the SWIR and red band are used to indicate the soil mineral composition. The blue and NIR are used to indicate the presence of vegetation. The BSI is than calculated (by normalising the bands bands) using the following formula:""")
st.latex(r"""
\text{BSI} = \frac{(\text{red} + \text{SWIR}) - (\text{NIR} + \text{blue})}{(\text{red} + \text{SWIR}) + (\text{NIR} + \text{blue})}
""")
paper_bsi_url = "https://doi.org/10.1016/j.isprsjprs.2023.03.016" 
st.write(f"""The drawback of only using BSI is discussed in [the paper of Castaldi et. al. (2023)]({paper_bsi_url}); important parts of the BSI are related to vegetation in a photosynthetizing state. However soils can also be covered by crop residue or mulch. In order to discriminate between such soils this paper uses the Normalized Burn Ratio 2 (NBR2). This index flags dry vegetation on the surface. The NBR is calcluated as follows with the Sentinel-2 SWIR1 (B11) and SWIR2 (B12) bands:""")
st.latex(r"""
\text{NBR2} = \frac{(B_{11} - B_{12})}{(B_{11} + B_{12})}
""")
st.write("In order to filter out soils with dry vegetation, the paper sets the following thresholds for each pixel to be considered truly bare; NDVI < 0.35, NBR2 < 0.125 and BSI < 0.021")
st.write("Below a chart is presented with 3 indices plotted together. The green circles indicate the dates if only BSI is considered, while the orange circles highlight the discriminating addition of NBR2. Please note that the BSI is calcualted using the Sentinel-2 bands B2,B4,B8 and B12. However, some BSI use Sentinel-2 B11 instead of B12, but the pattern remains similar""")
# read in BSI data and combine
df_bsi12 = load_bsi12_nop()
df_nbr = load_nbr_nop()
# Rename the NBR2 and BSI columns to differentiate them
df_nbr.rename(columns={'NBR2': 'value'}, inplace=True)
df_bsi12.rename(columns={'BSI': 'value'}, inplace=True)
df_ndvi.rename(columns={'NDVI': 'value'}, inplace=True)
# add index type to track which is NBR and which is BSI
df_nbr['index_type']='NBR2'
df_bsi12['index_type']='BSI'
df_ndvi['index_type'] = 'NDVI'
df_combined = pd.concat([df_nbr,df_bsi12,df_ndvi])
with st.expander("Toggle linked BSI12,NDVI and NBR2 plot",expanded=True):
    
    gid_to_plot = 1400841
    if map.get("last_object_clicked_tooltip"):
        gid_to_plot = get_gid_from_tooltip(map["last_object_clicked_tooltip"])
    if gid_to_plot is not None:
        # subselect data
        df_selection_combined = df_combined.loc[df_combined['gid'] == gid_to_plot]
        # pivot this table to filter indices all at once
        df_pivot = df_selection_combined.pivot_table(index=['date', 'gid'], columns='index_type', values='value').reset_index()
        df_pivot['highlight'] = (
            (df_pivot['NDVI'] < 0.35) &
            (df_pivot['NBR2'] < 0.125) &
            (df_pivot['BSI'] > 0.021)
        )
        df_pivot['highlight_bsi'] = (
            (df_pivot['BSI'] > 0.021) &
             ~df_pivot['highlight']
        )
        # Melt the pivoted DataFrame back to long format for plotting
        df_long = df_pivot.melt(id_vars=['date', 'gid', 'highlight', 'highlight_bsi'], value_vars=['NDVI', 'NBR2', 'BSI'], var_name='index_type', value_name='value')

        #df_selection_nbr = df_nbr.loc[df_nbr['gid'] == gid_to_plot]
        # Display line chart
        base_chart = alt.Chart(df_long).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('value:Q', title='Index value'),
                    tooltip=['date:T', 'value:Q', 'index_type:N'],
                    color='index_type:N'
                    )
        # add all different lines with lower opacity
        lines = base_chart.mark_line(point={
        "filled": False,
        "fill": "white"
        }).encode(opacity=alt.value(0.7))
        # add highlighted values with higher opacity
        highlight = base_chart.transform_filter(
            alt.datum.highlight == True
            ).mark_point(size=100).encode(
            color=alt.value('orange')  # Highlight selected data points in red
            )
        highlight_bsi = base_chart.transform_filter(
            alt.datum.highlight_bsi == True
            ).mark_point(size=100).encode(
            color=alt.value('green')  # Highlight selected data points in red
            )
        # combine two charts
        chart = (lines + highlight + highlight_bsi).properties(height=320,title=f'Chart of NDVI, BSI and NBR2 indices from Sentinel-2 reads for field {gid_to_plot}')
        #st.write(f'Chart of BSI,NDVI and NBR reads by Sentinel-2 for selected field {gid_to_plot}')
        st.altair_chart(chart.interactive(), use_container_width=True)

container = st.container(border=True)
container.write(f"**Conclusion**")
container.markdown(
    """
    **Plotting BSI together with NDVI and NBR2 reveals the following:**
    - **BSI and NDVI are highly (negatively) correlated**
    - **Introducing NBR2 as an indicator of dry vegetation presences reduces the ammount of soil labeled as bare (see green vs orange encircled points)**
    - **Plotting these indices gives a clear overview of presence of bare soils throughout the season**
    - **In terms of cadency the revisit frequency of Sentinel-2 seem sufficient to have at least a few measurements during the intervals where soil cover can be obliged**
    """)


df_GRD = load_GRD_parquet()
# add vv vh and RVI
df_GRD['VH/VV'] = df_GRD['VH']/df_GRD['VV']
df_GRD['RVI'] = (4*df_GRD['VH'])/(df_GRD['VH']+df_GRD['VV'])
df_GRD['RVI4S1'] = (df_GRD['VH/VV']*(df_GRD['VH/VV']+3))/((df_GRD['VH/VV']+1)*(df_GRD['VH/VV']+1))


with st.expander("Toggle linked Sentinel-1 GRD plot",expanded=True):
    # Define available polarizations
    select_options = ['VV', 'VH', 'RVI', 'VH/VV','RVI4S1']
    # Use multiselect to allow users to choose which series to plot
    # Set default selection to RVI and VH/VV
    selected_values = st.multiselect(
        'Select index or polarization to plot in the chart',
        options=select_options,
        default=['RVI4S1', 'VH/VV']
    )

    if map.get("last_object_clicked_tooltip"):
        gid_to_plot = get_gid_from_tooltip(map["last_object_clicked_tooltip"])
    if gid_to_plot is not None:
        # subselect data
        df_selection_GRD = df_GRD.loc[df_GRD['gid'] == gid_to_plot]
        
        #st.dataframe(data=df_selection_GRD_tf.head(20))
        # Melt the DataFrame to have a long format suitable for Altair
        df_melted = df_selection_GRD.melt(id_vars=['date', 'gid', 'orbit'], value_vars=selected_values, var_name='Polarization / Index', value_name='Value')
        # Create the Altair chart
        chart_grd = alt.Chart(df_melted).mark_line(point={
            "filled": False,
            "fill": "white"
        }).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('Value:Q', title='Value (dB) / Index'),
            color=alt.Color('orbit:N', title='Relative Orbit'),
            strokeDash='Polarization / Index',  # Different lines for VV and VH
        ).properties(height=320)
        
        
        st.write('Chart of Sentinel-1 reads and RVI VV/VH index seperated per orbit')
        st.altair_chart(chart_grd.interactive(), use_container_width=True)


df_COH = load_coh_csv()
with st.expander("Toggle coherence plot from Sentinel-1 reads",expanded=True):
    if map.get("last_object_clicked_tooltip"):
        gid_to_plot = get_gid_from_tooltip(map["last_object_clicked_tooltip"])
    if gid_to_plot is not None:
        # subselect data
        df_selection_COH = df_COH.loc[df_COH['gid'] == gid_to_plot]
        
        #min_COH = df_selection_COH_tf['RVI'].values.min()
        #max_COH = df_selection_COH_tf['RVI'].values.max()
        #st.dataframe(data=df_selection_GRD_tf.head(20))
        # Melt the DataFrame to have a long format suitable for Altair
        df_melted_tf_COH = df_selection_COH.melt(id_vars=['gid'],
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
        base_chart_COH = alt.Chart(df_melted_tf_COH).mark_line(point={
            "filled": False,
            "fill": "white"}).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('COH12:Q',scale = alt.Scale(domain=[40,110])),
            #scale=alt.Scale(domain=[min_RVI, max_RVI])), 
            color=alt.Color('Relative Orbit:N', title='Relative Orbit'),
            strokeDash='Polarization:N',
            detail='IW:N',
            
        ).properties(height=320).interactive()
        st.write(f'Chart of Sentinel-1 COH reads seperated per relative orbit and IW for field {gid_to_plot}')
        st.altair_chart(base_chart_COH.interactive(), use_container_width=True)


st.write(f"""Below the S2WI is plotted for the selected parcels above using the Sentinel-2 bands 2,4,8 and 11""")

# read in BSI data
df_s2wi = load_s2wi_nop()
with st.expander("Toggle linked S2WI plot",expanded=True):
    
    gid_to_plot = 1400841
    if map.get("last_object_clicked_tooltip"):
        gid_to_plot = get_gid_from_tooltip(map["last_object_clicked_tooltip"])
    if gid_to_plot is not None:
        # subselect data
        df_selection_s2wi = df_s2wi.loc[df_s2wi['gid'] == gid_to_plot]
        # Display line chart
        chart = alt.Chart(df_selection_s2wi).mark_line(point={
        "filled": False,
        "fill": "white"
        }).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('S2WI:Q', title='S2WI'),
                    #color='genre:N'
                    ).properties(height=320)
        st.write(f'Chart of S2WI reads by Sentinel-2 for selected field {gid_to_plot}')
        st.altair_chart(chart.interactive(), use_container_width=True)
