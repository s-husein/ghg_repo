from flask import Flask, send_from_directory, jsonify, request
import geopandas as gpd
import json
import requests

app = Flask(__name__)

STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

collection_name = "odiac-ffco2-monthgrid-v2023"
asset_name = "co2-emissions"

items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit=276").json()["features"]
items = {item["properties"]["start_datetime"][:7]: item for item in items}

rscl_vals = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"],
                  "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}

color_map = 'jet'

tile = requests.get(
    f"{RASTER_API_URL}/collections/{items['2022-12']['collection']}/items/{items['2022-12']['id']}/tilejson.json?"

    f"&assets={asset_name}"

    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

    f"&rescale={rscl_vals['min']},{rscl_vals['max']}", 

# Return the response in JSON format
).json()


def conv_json(json_obj):
    json_obj['type'] = "Feature"
    json_obj['properties'] = {}
    geom = json_obj['features'][0]['geometry']
    json_obj.pop("features")
    json_obj["geometry"] = geom
    


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


world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
# country_name = 'Pakistan'
# countryjson = json.loads(country.to_json())

# conv_json(countryjson)


@app.route("/get_country_stats", methods=['GET'])
def get_country_stats():
    data = {}
    country_name = request.args.get("country")
    data['date'] = request.args.get('date')
    country = world[world.name == country_name]
    countryjson = json.loads(country.to_json())
    tile = requests.get(
    f"{RASTER_API_URL}/collections/{items[data['date']]['collection']}/items/{items[data['date']]['id']}/tilejson.json?"
    f"&assets={asset_name}"
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
    f"&rescale={rscl_vals['min']},{rscl_vals['max']}", 
    ).json()

    data['tile'] = tile
    data['map'] = countryjson
    conv_json(countryjson)
    data['stats'] = generate_stats(items[data['date']], countryjson)['statistics']['b1']
    print(data['date'])
    return jsonify(data)

    

@app.route("/")
def index():
    return send_from_directory("", "test.html")


if __name__ == '__main__':
    app.run("0.0.0.0", 8000)