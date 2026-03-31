from flask import Flask, render_template, abort

app = Flask(__name__)

# Temporary sample data
REGULATORY_DATA = {
    "taiwan": {
        "name": "Taiwan 台湾",
        "categories": {
            "regulations": {
                "title": "Regulations ",
                "description": "Overview of Taiwanese UAV regulatory bodies and their responsibilities.",
                "subsections": [
                    {
                        "name": "CAA",
                        "summary": "Oversees UAV operations, flight safety, registration, and operational compliance."
                    },
                    {
                        "name": "BSMI",
                        "summary": "Handles standards, inspection, certification, and product compliance."
                    }
                ]
            },
            "testing": {
                "title": "Testing",
                "items": [
                    "EMC testing",
                    "RF testing"
                ]
            },
            "certifications": {
                "title": "Certifications",
                "items": [
                    "Product certification pathways",
                    "Compliance processes"
                ]
            },
            "export-controls": {
                "title": "Export Controls",
                "items": [
                    "Export documentation",
                    "Market-entry requirements"
                ]
            }
        }
    },
    "us": {
        "name": "United States 美国",
        "categories": {
            "regulations": {
                "title": "Regulations",
                "items": [
                    "FAA rules",
                    "FCC rules"
                ]
            },
            "testing": {
                "title": "Testing",
                "items": [
                    "RF compliance testing",
                    "Technical requirements"
                ]
            },
            "certifications": {
                "title": "Certifications",
                "items": [
                    "FAA approvals",
                    "FCC equipment authorization"
                ]
            },
            "export-controls": {
                "title": "Export Controls",
                "items": [
                    "Import rules",
                    "Export restrictions"
                ]
            }
        }
    },
    "eu": {
        "name": "European Union 欧洲联盟",
        "categories": {
            "regulations": {
                "title": "Regulations",
                "items": [
                    "EASA drone rules",
                    "Operational categories"
                ]
            },
            "testing": {
                "title": "Testing",
                "items": [
                    "Conformity assessment testing",
                    "Safety testing"
                ]
            },
            "certifications": {
                "title": "Certifications",
                "items": [
                    "CE-related pathways",
                    "EASA compliance requirements"
                ]
            },
            "export-controls": {
                "title": "Export Controls",
                "items": [
                    "Regional market requirements",
                    "Import/export considerations"
                ]
            }
        }
    }
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
        category=category
    )


if __name__ == "__main__":
    app.run(debug=True)