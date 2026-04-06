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
                "description": "Overview of Taiwanese UAV testing requirements and their procedures",
                "subsections": [
                    {
                        "name": "EMC testing",
                        "summary": "summary of EMC testing"
                    },
                    {
                        "name": "RF Testing",
                        "summary": "Summary of RF Testing"
                    }
                ]
            },
            "certifications": {
                "title": "Certifications",
                "description": "Overview of Taiwanese Certifications for UAVs",
                "subsections": [
                    {
                        "name": "Product certification pathways",
                        "summary": "summary"
                    },
                    {
                        "name": "Compliance Processes",
                        "summary": "summary"
                    }
                ]
            },
            "export-controls": {
                "title": "Export Controls",
                "description": "Overview of Taiwanese Export regulations and rules",
                "subsections": [
                    {
                        "name": "Export Documentation",
                        "summary": "summary"
                    },
                    {
                        "name": "Market-entry requirements",
                        "summary": "summary"
                    }
                ]
            }
        }
    },
    "us": {
        "name": "United States 美国",
        "categories": {
            "regulations": {
                "title": "Regulations",
                "description": "Overview of United States UAV regulatory bodies and their responsibilities.",
                "subsections": [
                    {
                        "name": "FAA",
                        "summary": "summary"
                    },
                    {
                        "name": "FCC",
                        "summary": "summary"
                    }
                ]
            },
            "testing": {
                "title": "Testing",
                "description": "Overview of United States UAV testing requirements and procedures.",
                "subsections": [
                    {
                        "name": "RF compliance testing",
                        "summary": "summary"
                    },
                    {
                        "name": "Technical requirements",
                        "summary": "summary"
                    }
                ]
            },
            "certifications": {
                "title": "Certifications",
                "description": "Overview of United States certifications and approval pathways for UAVs.",
                "subsections": [
                    {
                        "name": "FAA approvals",
                        "summary": "summary"
                    },
                    {
                        "name": "FCC equipment authorization",
                        "summary": "summary"
                    }
                ]
            },
            "export-controls": {
                "title": "Export Controls",
                "description": "Overview of United States import, export, and market-entry requirements for UAVs.",
                "subsections": [
                    {
                        "name": "Import rules",
                        "summary": "summary"
                    },
                    {
                        "name": "Export restrictions",
                        "summary": "summary"
                    }
                ]
            }
        }
    },
    "eu": {
        "name": "European Union 欧洲联盟",
        "categories": {
            "regulations": {
                "title": "Regulations",
                "description": "Overview of European Union UAV regulatory bodies and their responsibilities.",
                "subsections": [
                    {
                        "name": "EASA",
                        "summary": "summary"
                    },
                    {
                        "name": "Operational categories",
                        "summary": "summary"
                    }
                ]
            },
            "testing": {
                "title": "Testing",
                "description": "Overview of European Union UAV testing requirements and procedures.",
                "subsections": [
                    {
                        "name": "Conformity assessment testing",
                        "summary": "summary"
                    },
                    {
                        "name": "Safety testing",
                        "summary": "summary"
                    }
                ]
            },
            "certifications": {
                "title": "Certifications",
                "description": "Overview of European Union certifications and compliance pathways for UAVs.",
                "subsections": [
                    {
                        "name": "CE-related pathways",
                        "summary": "summary"
                    },
                    {
                        "name": "EASA compliance requirements",
                        "summary": "summary"
                    }
                ]
            },
            "export-controls": {
                "title": "Export Controls",
                "description": "Overview of European Union market-entry, import, and export considerations for UAVs.",
                "subsections": [
                    {
                        "name": "Regional market requirements",
                        "summary": "summary"
                    },
                    {
                        "name": "Import/export considerations",
                        "summary": "summary"
                    }
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
        category=category,
        category_key=category_key
    )

@app.route("/region/<region_key>/<category_key>/<int:subsection_index>")
def subsection_page(region_key, category_key, subsection_index):
    region = REGULATORY_DATA.get(region_key)
    if not region:
        abort(404)

    category = region["categories"].get(category_key)
    if not category:
        abort(404)

    subsections = category.get("subsections", [])
    if subsection_index < 0 or subsection_index >= len(subsections):
        abort(404)

    subsection = subsections[subsection_index]

    return render_template(
        "subsection.html",
        region=region,
        region_key=region_key,
        category=category,
        category_key=category_key,
        subsection=subsection,
        subsection_index=subsection_index
    )


if __name__ == "__main__":
    app.run(debug=True)