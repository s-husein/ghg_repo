import requests
import folium
import folium.plugins
from folium import Map, TileLayer
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, send_from_directory
import json
import geopandas as gpd

app = Flask(__name__)

def generate_stats(item, geojson):

    result = requests.post(
        f"{RASTER_API_URL}/cog/statistics",
        params={"url": item["assets"][asset_name]["href"]},
        json=geojson,
    ).json()
    return {
        **result["properties"],
        "start_datetime": item["properties"]["start_datetime"][:7],
    }

def get_item_count(collection_id):
    global STAC_API_URL

    count = 0
    items_url = f"{STAC_API_URL}/collections/{collection_id}/items"
    while True:
        response = requests.get(items_url)
        if not response.ok:
            print("error getting items")
            exit()
        stac = response.json()
        count += int(stac["context"].get("returned", 0))

        next = [link for link in stac["links"] if link["rel"] == "next"]

        if not next:
            break
        
        items_url = next[0]["href"]

    return count

def conv_json(json_obj):
    json_obj['type'] = "Feature"
    json_obj['properties'] = {}
    geom = json_obj['features'][0]['geometry']
    json_obj.pop("features")
    json_obj["geometry"] = geom


STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

collection_name = "odiac-ffco2-monthgrid-v2023"

num_items = 276

items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={num_items}").json()["features"]
items = {item["properties"]["start_datetime"][:7]: item for item in items}
asset_name = "co2-emissions"


rscl_vals = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"],
                  "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}

color_map = "rainbow"

tile = requests.get(
    f"{RASTER_API_URL}/collections/{items['2022-12']['collection']}/items/{items['2022-12']['id']}/tilejson.json?"

    f"&assets={asset_name}"

    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

    f"&rescale={rscl_vals['min']},{rscl_vals['max']}", 

# Return the response in JSON format
).json()
zoom = 11




world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
country_name = 'Pakistan'
country = world[world.name == country_name]
countryjson = json.loads(country.to_json())

conv_json(countryjson)



items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={num_items}").json()["features"]

# stats = [generate_stats(item, countryjson) for item in items]
stats = generate_stats(items[0], countryjson)


print(stats)

e_offset = 0.18018
n_offset = 0.108108
quetta = (30.1834, 66.9987)

@app.route("/")
def index():
    map_ = Map(quetta, zoom_start=zoom)
                    #   dragging=False,
                    #   max_bounds=True,
                    #   min_zoom=zoom,
                    #   max_zoom=zoom)

# Define the first map layer (January 2020)
    # co2_layer = TileLayer(
    #     tiles=tile["tiles"][0], # Path to retrieve the tile
    #     attr="GHG", # Set the attribution
    #     opacity=0.7, # Adjust the transparency of the layer
    #     min_zoom=zoom,
    #     max_zoom=zoom,
    # )
    

    # Add the country border as a polygon on the map
    folium.GeoJson(
        country,
        style_function=lambda x: {
            'fillColor': 'lightblue',
            'color': 'blue',
            'weight': 2,
            'fillOpacity': 0.5,
        }
    ).add_to(map_)

    # co2_layer.add_to(map_)


    map_.save("map.html")
    return send_from_directory("", 'map.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)