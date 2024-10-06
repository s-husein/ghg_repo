from flask import Flask, send_from_directory, jsonify, request
import geopandas as gpd
import json
import requests

app = Flask(__name__)

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

STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

collection_name = "odiac-ffco2-monthgrid-v2023"
asset_name = "co2-emissions"

items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit=276").json()["features"]

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
# country_name = 'Pakistan'
# countryjson = json.loads(country.to_json())

# conv_json(countryjson)


@app.route("/get_country_boundary", methods=['GET'])
def get_country_boundary():
    country_name = request.args.get('country')
    country = world[world.name == country_name]
    return country.to_json()

@app.route("/get_country_stats", methods=['GET'])
def get_country_stats():
    data = {}
    country_name = request.args.get("country")
    data['date'] = request.args.get('date')
    country = world[world.name == country_name]
    countryjson = json.loads(country.to_json())
    data['map'] = countryjson
    conv_json(countryjson)
    data['stats'] = generate_stats(items[0], countryjson)['statistics']['b1']
    print(data['date'])
    return jsonify(data)

    

@app.route("/")
def index():
    return send_from_directory("", "test.html")


if __name__ == '__main__':
    app.run("0.0.0.0", 8000)