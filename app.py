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
                        "summary": "summary of EMC testing",
                        "entries": [
                            {
                                "region": "Taiwan",
                                "primary_category": "Electromagnetic Capability (EMC)",
                                "secondary_category": "Electromagnetic interference (EMI)",
                                "topic": "EMC structure and EMI definitions used in Taiwan drone testing",
                                "source_title": "Electromagnetic Compatibility (EMC) for Drone Testing",
                                "brief_summary": "ETC EMC deck defines EMC as EMI plus EMS and explicitly separates conducted emission, radiated emission, conducted susceptibility, and radiated susceptibility; it frames EMI as electromagnetic energy emitted through radiation or conduction that interferes with other equipment.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            },
                            {
                                "region": "Taiwan",
                                "primary_category": "Electromagnetic Capability (EMC)",
                                "secondary_category": "Electromagnetic susceptibility / immunity",
                                "topic": "Taiwan drone immunity framework using CNS / IEC standards",
                                "source_title": "Electromagnetic Compatibility (EMC) for Drone Testing",
                                "brief_summary": "ETC EMC deck shows Taiwan drone immunity testing tied to CNS 16197 (CISPR 35), CNS 14674-2 (IEC 61000-6-2), and the specific IEC 61000-4-x immunity families, making Taiwan much more explicit on immunity than the earlier workbook version suggested.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            },
                            {
                                "region": "Taiwan",
                                "primary_category": "Electromagnetic Capability (EMC)",
                                "secondary_category": "Electrostatic discharge (ESD)",
                                "topic": "Taiwan drone ESD test requirement",
                                "source_title": "Electromagnetic Compatibility (EMC) for Drone Testing",
                                "brief_summary": "ETC EMC deck lists CNS 14676-2 (IEC 61000-4-2) as the ESD test method and, for under-2 kg drones, shows ESD performance criteria of contact discharge 4 kV and air discharge 8 kV.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            },
                            {
                                "region": "Taiwan",
                                "primary_category": "Electromagnetic Capability (EMC)",
                                "secondary_category": "Radiated susceptibility / immunity",
                                "topic": "Taiwan radiated immunity / radiated susceptibility requirements for drones",
                                "source_title": "Electromagnetic Compatibility (EMC) for Drone Testing",
                                "brief_summary": "ETC EMC deck maps radiated immunity to CNS 14676-3 (IEC 61000-4-3). For under-2 kg drones it shows 80 MHz-1 GHz at 10 V/m and 1.4-6.0 GHz at 3 V/m with 80% AM; for 2-25 kg drones it describes propeller-off, motor-speed stability testing in an anechoic chamber with a 10 percent fluctuation limit and no loss of function.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            }
                    
                        ]
                    },
                    {
                        "name": "RF Testing",
                        "summary": "Summary of RF Testing",
                        "entries": [
                            {
                                "region": "Taiwan",
                                "primary_category": "Radio Frequency (RF)",
                                "secondary_category": "Wireless RF testing standards",
                                "topic": "NCC RF type-approval framework for low-power and telecom radio devices",
                                "source_title": "Introduction to Wireless RF: an ETC Provided PDF, Page 4",
                                "brief_summary": "ETC RF deck maps Taiwan NCC RF regulation families used for wireless products, including LP0002 for low-power radio-frequency devices, RTTE01 for 2.4 GHz radio-frequency telecommunications terminal equipment, and IS2031-0 for point-to-point microwave radio-frequency equipment.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            }
                        ]
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
                        "name": "Technical requirements",
                        "summary": "summary"
                    },
                    {
                        "name": "RF Compliance Testing",
                        "summary": "Summary of RF Testing",
                        "entries": [
                            {
                                "region": "United States",
                                "primary_category": "Radio Frequency (RF)",
                                "secondary_category": "Wireless RF testing standards",
                                "topic": "FCC RF rule families and test methods used for wireless devices",
                                "source_title": "Introduction to Wireless RF: an ETC Provided PDF, Page 5",
                                "brief_summary": "ETC RF deck maps U.S. FCC RF rule families and matching test methods, including Part 15 Subpart B with ANSI C63.4-2014, Part 15 Subpart C with ANSI C63.10-2013, Part 15 Subpart D with ANSI C63.17-2013, and Part 15 Subpart E / DFS with FCC KDB 905462.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            },
                            {
                                "region": "United States",
                                "primary_category": "Radio Frequency (RF)",
                                "secondary_category": "Bluetooth modulation / channelization",
                                "topic": "Bluetooth FCC test items for 2.4 GHz modules",
                                "source_title": "Introduction to Wireless RF: an ETC Provided PDF, Page 8",
                                "brief_summary": "ETC RF deck lists Bluetooth-related FCC test items including radiated emission, conducted emission, antenna requirement, 20 dB emission bandwidth, output power, out-of-band conducted spurious emissions, hopping-channel count and spacing, dwell time, and maximum permissible exposure under Part 15.247 / 15.207 / 15.203 / 2.1093.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            },
                            {
                                "region": "United States",
                                "primary_category": "Radio Frequency (RF)",
                                "secondary_category": "Wireless RF testing standards",
                                "topic": "Wi-Fi / U-NII / DFS channel-plan testing context",
                                "source_title": "Introduction to Wireless RF: an ETC Provided PDF, Page 8",
                                "brief_summary": "ETC RF deck includes IEEE 802.11 a/b/g/n/ac/ax references, U-NII channel-plan context under §15.407, and DFS-related testing context via FCC KDB 905462, which is directly relevant to drone Wi-Fi, telemetry, and video links using 2.4 GHz / 5 GHz radios.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            }
                        ]
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
                        "name": "Technical requirements",
                        "summary": "summary"
                    },
                    {
                        "name": "Safety testing",
                        "summary": "summary"
                    },
                    {
                        "name": "RF Compliance Testing",
                        "summary": "Summary of RF Testing",
                        "entries": [
                            {
                                "region": "European Union",
                                "primary_category": "Radio Frequency (RF)",
                                "secondary_category": "RED RF regulations",
                                "topic": "RED RF standards stack for common short-range and broadband wireless devices",
                                "source_title": "Introduction to Wireless RF: an ETC Provided PDF, Page 6",
                                "brief_summary": "ETC RF deck maps the EU RED standards stack, including ETSI EN 300 220, EN 300 330, EN 300 440, EN 300 328, EN 301 893, EN 302 502, EN 301 357, and ERC Recommendation 70-03 for short-range, wideband, and 5 GHz systems.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            },
                            {
                                "region": "European Union",
                                "primary_category": "Radio Frequency (RF)",
                                "secondary_category": "Bluetooth modulation / channelization",
                                "topic": "Bluetooth modulation modes and channel plans used in RF evaluation",
                                "source_title": "Introduction to Wireless RF: an ETC Provided PDF, Page 6",
                                "brief_summary": "ETC RF deck summarizes Bluetooth modulation modes relevant to RF evaluation: Bluetooth 2.1+EDR uses GFSK, pi/4-DQPSK, and 8-DPSK, while Bluetooth LE uses GFSK; the deck also shows BR/EDR and LE channel-list examples and 20 dB emission-bandwidth examples.",
                                "pdf_url": "/static/pdfs/introduction_to_wireless_rf.pdf"
                            }
                        ]
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