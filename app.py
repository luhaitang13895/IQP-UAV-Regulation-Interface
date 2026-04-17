import json
from pathlib import Path
from flask import Flask, render_template, abort, request
from keywordSearch import keywordSearch

app = Flask(__name__)

def load_json(filename):
    file_path = Path("data") / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def getRegulatoryData ():
    REGULATORY_DATA = {
        "taiwan": load_json("taiwan.json"),
        "us": load_json("us.json"),
        "eu": load_json("eu.json")
    }
    return REGULATORY_DATA



@app.route("/")
def home():
    return render_template("home.html", regions=getRegulatoryData())


@app.route("/region/<region_key>")
def region_page(region_key):
    region = getRegulatoryData().get(region_key)
    if not region:
        abort(404)
    return render_template("region.html", region=region, region_key=region_key)


@app.route("/region/<region_key>/topic/<topic_key>")
def topic_page(region_key, topic_key):
    region = getRegulatoryData().get(region_key)
    if not region:
        abort(404)

    topic = region.get("topics", {}).get(topic_key)
    if not topic:
        abort(404)

    return render_template(
        "topic.html",
        region=region,
        region_key=region_key,
        topic=topic,
        topic_key=topic_key
    )


@app.route("/region/<region_key>/topic/<topic_key>/category/<category_key>")
def category_page(region_key, topic_key, category_key):
    region = getRegulatoryData().get(region_key)
    if not region:
        abort(404)

    topic = region.get("topics", {}).get(topic_key)
    if not topic:
        abort(404)

    category = topic.get("categories", {}).get(category_key)
    if not category:
        abort(404)

    return render_template(
        "category.html",
        region=region,
        region_key=region_key,
        topic=topic,
        topic_key=topic_key,
        category=category,
        category_key=category_key
    )

@app.route("/search")
def search():
    keyword = request.args.get("keyword")
    if not keyword:
        abort(400, description="Missing required parameter: keyword")

    
    selectedRegions = request.args.getlist("regions")

    allRegions = getRegulatoryData().keys()

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

@app.route("/region/<region_key>/topic/<topic_key>/category/<category_key>/subsection/<subsection_slug>")
def subsection_page(region_key, topic_key, category_key, subsection_slug):
    region = getRegulatoryData().get(region_key)
    if not region:
        abort(404)

    topic = region.get("topics", {}).get(topic_key)
    if not topic:
        abort(404)

    category = topic.get("categories", {}).get(category_key)
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
        topic=topic,
        topic_key=topic_key,
        category=category,
        category_key=category_key,
        subsection=subsection
    )

@app.route('/addNewEntry', methods=['POST'])
def addNewEntry ():
    try:
        print('adding new entry')
        data = json.loads(request.get_json())

        regionName = data.get('region')
        primaryCategory = data.get('primary_category')
        secondaryCategory = data.get('secondary_category')
        sourceTitle = data.get('source_title')
        briefSummary = data.get('brief_summary')
        externalURL = data.get('external_url', '')
        pdfLink = data.get('pdf_link', '')

        dataToAppend = {
            "region": regionName,
            "primary_category": primaryCategory,
            "secondary_category": secondaryCategory,
            "source_title": sourceTitle,
            "brief_summary": briefSummary,
            "externalURL": externalURL,
            "pdfLink": pdfLink
        }

        regionKey = data.get('region_key')
        regionJson = load_json(regionKey + ".json")

        topicKey = data.get('topic_key')
        categoryKey = data.get('category_key')

        # Becasue subsections are a list, we need to find the index of the subsection by slug
        subsectionSlug = data.get('subsection_slug')
        categorySubsections = regionJson['topics'][topicKey]['categories'][categoryKey]["subsections"]
        subsectionIndex = 0
        # Loops through all subsections to match slug
        for subsection in categorySubsections:
            if subsection['slug'] == subsectionSlug: break
            subsectionIndex += 1

        # Adds the entry to the json:
        regionJson['topics'][topicKey]['categories'][categoryKey]["subsections"][subsectionIndex]['entries'].append(dataToAppend)
        
        # Saves the new json
        filepath = "data/" + regionKey + ".json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(regionJson, f, indent=2)


        print('sucessfully added to form')
        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}

if __name__ == "__main__":
    app.run(debug=True)