import json
from pathlib import Path
from flask import Flask, render_template, abort, request
from keywordSearch import keywordSearch

app = Flask(__name__)

def load_json(filename):
    file_path = Path("data") / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

REGULATORY_DATA = {
    "taiwan": load_json("taiwan.json"),
    "us": load_json("us.json"),
    "eu": load_json("eu.json")
}

@app.route("/")
def home():
    return render_template("home.html", regions=REGULATORY_DATA)


@app.route("/region/<region_key>")
def region_page(region_key):
    region = REGULATORY_DATA.get(region_key)
    if not region:
        abort(404)
    return render_template("region.html", region=region, region_key=region_key)


@app.route("/region/<region_key>/<category_key>")
def category_page(region_key, category_key):
    region = REGULATORY_DATA.get(region_key)
    if not region:
        abort(404)

    category = region["categories"].get(category_key)
    if not category:
        abort(404)

    return render_template(
        "category.html",
        region=region,
        region_key=region_key,
        category=category,
        category_key=category_key
    )

@app.route("/search")
def search():
    keyword = request.args.get("keyword")
    if not keyword:
        abort(400, description="Missing required parameter: keyword")

    
    selectedRegions = request.args.getlist("regions")

    allRegions = REGULATORY_DATA.keys()

    results = keywordSearch(keyword, regions = selectedRegions)

    # for result in results:
    #     print("=" * 80)
    #     print("RESULT:")
    #     print(result)
    #     link = "http://127.0.0.1:5000" + result.get("path", "")
    #     print(link)

    return render_template(
        "search.html",
        results=results,
        keyword=keyword,
        allRegions = allRegions,
        selectedRegions = selectedRegions
    )

@app.route("/region/<region_key>/<category_key>/<subsection_slug>")
def subsection_page(region_key, category_key, subsection_slug):
    region = REGULATORY_DATA.get(region_key)
    if not region:
        abort(404)

    category = region["categories"].get(category_key)
    if not category:
        abort(404)

    subsection = None
    for section in category.get("subsections", []):
        if section.get("slug") == subsection_slug:
            subsection = section
            break

    if not subsection:
        abort(404)

    return render_template(
        "subsection.html",
        region=region,
        region_key=region_key,
        category=category,
        category_key=category_key,
        subsection=subsection
    )


if __name__ == "__main__":
    app.run(debug=True)