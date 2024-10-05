import requests
import folium
import folium.plugins
from folium import Map, TileLayer
from pystac_client import Client
import branca
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, send_from_directory

app = Flask(__name__)
# def get_item_count(collection_id):
#     global STAC_API_URL

#     count = 0
#     items_url = f"{STAC_API_URL}/collections/{collection_id}/items"

#     # Run a while loop to make HTTP requests until there are no more URLs associated with the collection in the STAC API
#     while True:
#         response = requests.get(items_url)

#         # If the items do not exist, print an error message and quit the loop
#         if not response.ok:
#             print("error getting items")
#             exit()

#         # Return the results of the HTTP response as JSON
#         stac = response.json()

#         # Increase the "count" by the number of items (granules) returned in the response
#         count += int(stac["context"].get("returned", 0))

#         # Retrieve information about the next URL associated with the collection in the STAC API (if applicable)
#         next = [link for link in stac["links"] if link["rel"] == "next"]

#         # Exit the loop if there are no other URLs
#         if not next:
#             break
        
#         # Ensure the information gathered by other STAC API links associated with the collection are added to the original path
#         # "href" is the identifier for each of the tiles stored in the STAC API
#         items_url = next[0]["href"]

#     # Return the information about the total number of granules found associated with the collection
#     return count

# STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

# # The RASTER API is used to fetch collections for visualization
# RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

# # The collection name is used to fetch the dataset from the STAC API. First, we define the collection name as a variable
# # Name of the collection for ODIAC dataset 
# collection_name = "odiac-ffco2-monthgrid-v2023"
# collection = requests.get(f"{STAC_API_URL}/collections/{collection_name}").json()
# num_items = get_item_count(collection_name)
# items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={num_items}").json()["features"]
# items = {item["properties"]["start_datetime"][:7]: item for item in items}
# asset_name = "co2-emissions"
# rescale_values = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}
# color_map = "rainbow" 

# # Make a GET request to retrieve information for the 2020 tile
# # 2020
# january_2020_tile = requests.get(

#     # Pass the collection name, the item number in the list, and its ID
#     f"{RASTER_API_URL}/collections/{items['2020-01']['collection']}/items/{items['2020-01']['id']}/tilejson.json?"

#     # Pass the asset name
#     f"&assets={asset_name}"

#     # Pass the color formula and colormap for custom visualization
#     f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

#     # Pass the minimum and maximum values for rescaling
#     f"&rescale={rescale_values['min']},{rescale_values['max']}", 

# # Return the response in JSON format
# ).json()
# january_2000_tile = requests.get(

#     # Pass the collection name, the item number in the list, and its ID
#     f"{RASTER_API_URL}/collections/{items['2000-01']['collection']}/items/{items['2000-01']['id']}/tilejson.json?"

#     # Pass the asset name
#     f"&assets={asset_name}"

#     # Pass the color formula and colormap for custom visualization
#     f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

#     # Pass the minimum and maximum values for rescaling
#     f"&rescale={rescale_values['min']},{rescale_values['max']}", 

# # Return the response in JSON format
# ).json()

e_offset = 0.18018
n_offset = 0.108108
quetta = (30.1834, 66.9987)
top_left = (quetta[0]+n_offset, quetta[1]-e_offset)
top_right = (quetta[0]+n_offset, quetta[1]+e_offset)
bot_left = (quetta[0]-n_offset, quetta[1]-e_offset)
bot_right = (quetta[0]-n_offset, quetta[1]+e_offset)

@app.route("/")
def index():
    
    map_ = folium.Map(quetta, zoom_start=11,
                      dragging=False,
                      max_bounds=True,
                      min_zoom=11,
                      max_zoom=13)

# Define the first map layer (January 2020)
    # map_layer_2020 = TileLayer(
    #     tiles=january_2020_tile["tiles"][0], # Path to retrieve the tile
    #     attr="GHG", # Set the attribution
    #     opacity=0.8, # Adjust the transparency of the layer
    # )

    # folium.Marker(location=q,
    #               popup="quetta").add_to(map_)
    # Add the first layer to the Dual Map
    # map_layer_2020.add_to(map_)

    # # Define the second map layer (January 2000)
    # map_layer_2000 = TileLayer(
    #     tiles=january_2000_tile["tiles"][0], # Path to retrieve the tile
    #     attr="GHG", # Set the attribution
    #     opacity=0.8, # Adjust the transparency of the layer
    # )

    # map_layer_2000.add_to(map_)
    map_.save("map.html")
    return send_from_directory("", 'map.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)