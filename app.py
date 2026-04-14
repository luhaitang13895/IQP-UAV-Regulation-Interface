import json
from pathlib import Path
from flask import Flask, render_template, abort

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


@app.route("/region/<region_key>/topic/<topic_key>")
def topic_page(region_key, topic_key):
    region = REGULATORY_DATA.get(region_key)
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
    region = REGULATORY_DATA.get(region_key)
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


@app.route("/region/<region_key>/topic/<topic_key>/category/<category_key>/subsection/<subsection_slug>")
def subsection_page(region_key, topic_key, category_key, subsection_slug):
    region = REGULATORY_DATA.get(region_key)
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


if __name__ == "__main__":
    app.run(debug=True)