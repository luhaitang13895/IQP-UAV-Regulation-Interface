import json
from pathlib import Path
from flask import Flask, render_template, abort, request, session, redirect, url_for, flash
from keywordSearch import keywordSearch
import os
from functools import wraps
import subprocess
import threading
import time
import requests

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-this-password")

global changesMade 
changesMade = False

# NOT DOING THIS ANYMORE:
# Variables relating to the timer/ping system
# SELF_PING_URL = 'https://etc-uav-regulation-interface.onrender.com/ping'
# SYNC_DELAY_SECONDS = 15 * 60 # how long to wait before pushing changes to github
# PING_INTERVAL_SECONDS = 60

# timerLock = threading.Lock()
# lastDataUpdateTime = None
# syncWorkerRunning = False

# pushes the code to main on git
def commitAndPush():
    try:
        subprocess.run(["git", "add", "data"], check=True)

        # Don't commit if there are no changes
        diffResult = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diffResult.returncode == 0:
            print("No JSON changes to commit.")
            return True

        subprocess.run(["git", "commit", "-m", "auto-update json"], check=True)
        subprocess.run(["git", "push"], check=True)

        print("Successfully pushed JSON changes to Git.")
        return True
    except Exception as e:
        print("Git push failed:", e)
        return False
    
# THESE FUNCTIONS ARE WICKED COMPLICATED AND PROBABLY SHOULDNT BE USED

# Worker thread function (counts down to 15 minutes and sends the message - pings every 1 minute to keep the instance alive)
# def dataSyncWorker():
#     global lastDataUpdateTime
#     global syncWorkerRunning
#     print("Data sync worker started.")

#     timesTriedToSync = 0
#     while True:
#         time.sleep(PING_INTERVAL_SECONDS)

#         try:
#             requests.get(SELF_PING_URL, timeout=10)
#             print("Pinged self to stay awake.")
#         except Exception as e:
#             print("Self-ping failed:", e)

#         # Blocks the main thread from updating any variables and crashing out
#         timerLock.acquire()
#         try:
#             secondsSinceLastUpdate = time.time() - lastDataUpdateTime
#             if secondsSinceLastUpdate > SYNC_DELAY_SECONDS:
#                 print("enough time passed with no edits. Syncing to Git...")
#                 gitPushSuccess = commitAndPush()
#                 if gitPushSuccess:
#                     lastDataUpdateTime = None
#                     syncWorkerRunning = False
#                     print("Sync complete. Worker stopping.")
#                     return
#                 else:
#                     if timesTriedToSync < 4:
#                     # If push failed, try again after another minute
#                         print("Sync failed. Will retry.")
#                     else:
#                         # Otherwise stop trying to sync (data will be lost but it wont drain the account of free instance hours)
#                         syncWorkerRunning = False
#                         return
#                     timesTriedToSync += 1
#         finally:
#             timerLock.release()

# # This is the function that is called whenever the data gets updated
# def updateDataTimer ():
#     global lastDataUpdateTime
#     global syncWorkerRunning

#     timerLock.acquire()
#     try:
#         lastDataUpdateTime = time.time() # This varaible is what keeps track of when the last update was made
#         if not syncWorkerRunning:
#             syncWorkerRunning = True
#             workerThread = threading.Thread(target=dataSyncWorker, daemon=True)
#             workerThread.start()
#             print("Started new sync timer.")
#         else:
#             print("Reset existing sync timer.")
#     finally:
#         timerLock.release()


def is_admin():
    return session.get("is_admin", False)

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_admin():
            return {"success": False, "error": "Unauthorized"}, 401
        return func(*args, **kwargs)
    return wrapper

@app.route("/ping")
def ping():
    return {"success": True}

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Logged in successfully.")
            return redirect(url_for("home"))
        else:
            flash("Incorrect password.")
            
    global changesMade
    # ^ just for consistency with the headers
    return render_template("admin_login.html", is_admin=is_admin(), changesMade=changesMade)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("home"))

@app.route("/admin/pushChanges", methods=["POST"])
@admin_required
def pushChanges ():
    try:
        pushed = commitAndPush()
        if not pushed:
            raise Exception ('Commit Failed :(')
        global changesMade
        changesMade = False
        return {"success": True}
    except Exception as e:
        print('ERROR PUSHING DATA')
        print(e)
        return {"success": False}

def load_json(filename):
    file_path = Path("data") / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def getRegulatoryData ():
    jsonFileNames = os.listdir('./data')
    REGULATORY_DATA = {}
    for filename in jsonFileNames:
        try: # try is incase the load json fails (happens if the json file isnt a real json)
            shorthand = filename[0:-5]
            REGULATORY_DATA[shorthand] = load_json(filename)
        except Exception as e:
            print('ERROR LOADING: ', filename)

    # REGULATORY_DATA = {
    #     "taiwan": load_json("taiwan.json"),
    #     "us": load_json("us.json"),
    #     "eu": load_json("eu.json")
    # }
    return REGULATORY_DATA


# Gets the subsection index from a given slug
def getSubsectionIndexFromSlug (slug, subsections):
    index = 0
    # Loops through all subsections to match slug
    for subsection in subsections:
        if subsection['slug'] == slug: return index
        index += 1
    return -1

@app.route("/")
def home():
    global changesMade
    return render_template("home.html", regions=getRegulatoryData(), is_admin=is_admin(), changesMade=changesMade)


@app.route("/region/<region_key>")
def region_page(region_key):
    region = getRegulatoryData().get(region_key)
    if not region:
        abort(404)
    global changesMade
    return render_template("region.html", region=region, region_key=region_key, is_admin=is_admin(), changesMade=changesMade)


@app.route("/region/<region_key>/topic/<topic_key>")
def topic_page(region_key, topic_key):
    region = getRegulatoryData().get(region_key)
    if not region:
        abort(404)

    topic = region.get("topics", {}).get(topic_key)
    if not topic:
        abort(404)

    global changesMade
    return render_template(
        "topic.html",
        region=region,
        region_key=region_key,
        topic=topic,
        topic_key=topic_key,
        is_admin=is_admin(), 
        changesMade=changesMade
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

    global changesMade
    return render_template(
        "category.html",
        region=region,
        region_key=region_key,
        topic=topic,
        topic_key=topic_key,
        category=category,
        category_key=category_key,
        is_admin=is_admin(), changesMade=changesMade
    )

@app.route("/search")
def search():
    keyword = request.args.get("keyword")
    if not keyword:
        abort(400, description="Missing required parameter: keyword")

    selectedRegions = request.args.getlist("regions")

    regulatoryData = getRegulatoryData()

    allRegions = [
        {
            "slug": slug,
            "name": regionData.get("name", slug)
        }
        for slug, regionData in regulatoryData.items()
    ]

    results = keywordSearch(keyword, regions=selectedRegions)

    global changesMade
    return render_template(
        "search.html",
        results=results,
        keyword=keyword,
        allRegions=allRegions,
        selectedRegions=selectedRegions,
        changesMade = changesMade
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

    global changesMade
    return render_template(
        "subsection.html",
        region=region,
        region_key=region_key,
        topic=topic,
        topic_key=topic_key,
        category=category,
        category_key=category_key,
        subsection=subsection,
        changesMade = changesMade,
        is_admin=is_admin()
    )

@app.route('/addNewEntry', methods=['POST'])
@admin_required
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
        regulationDate = data.get('date', '')

        dataToAppend = {
            "region": regionName,
            "primary_category": primaryCategory,
            "secondary_category": secondaryCategory,
            "source_title": sourceTitle,
            "brief_summary": briefSummary,
            "external_url": externalURL,
            "pdf_url": pdfLink,
            "regulation_date": regulationDate,
        }

        regionKey = data.get('region_key')
        regionJson = load_json(regionKey + ".json")

        topicKey = data.get('topic_key')
        categoryKey = data.get('category_key')

        # Becasue subsections are a list, we need to find the index of the subsection by slug
        subsectionSlug = data.get('subsection_slug')
        categorySubsections = regionJson['topics'][topicKey]['categories'][categoryKey]["subsections"]
        subsectionIndex = getSubsectionIndexFromSlug(subsectionSlug, categorySubsections)

        # Adds the entry to the json:
        regionJson['topics'][topicKey]['categories'][categoryKey]["subsections"][subsectionIndex]['entries'].append(dataToAppend)
        
        # Saves the new json
        filepath = "data/" + regionKey + ".json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(regionJson, f, indent=2)

        global changesMade
        changesMade = True

        print('sucessfully added to form')
        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}
    
@app.route('/addNewSubsection', methods=['POST'])
@admin_required
def addNewSubsection ():
    try:

        print('adding new subsection')
        data = json.loads(request.get_json())

        slug = data.get('subsection-slug')
        name = data.get('subsection-name')
        summary = data.get('subsection_summary')

        dataToAppend = {
            "slug": slug,
            "name": name,
            "summary": summary,
            "entries": []
        }

        print(dataToAppend)

        regionKey = data.get('region_key')
        regionJson = load_json(regionKey + ".json")

        topicKey = data.get('topic_key')
        categoryKey = data.get('category_key')

        # Checks to make sure the slug hasn't been used befores
        subsectionSlug = data.get('subsection_slug')
        categorySubsections = regionJson['topics'][topicKey]['categories'][categoryKey]["subsections"]
        subsectionIndex = getSubsectionIndexFromSlug (subsectionSlug,categorySubsections) # should return -1 for new slug
        if subsectionIndex > -1:
            raise Exception ('slug already used')

        # Adds the entry to the json:
        regionJson['topics'][topicKey]['categories'][categoryKey]["subsections"].append(dataToAppend)
        
        # Saves the new json
        filepath = "data/" + regionKey + ".json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(regionJson, f, indent=2)


        global changesMade
        changesMade = True
        print('sucessfully added to form')
        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}

@app.route('/addNewCategory', methods=['POST'])
@admin_required
def addCategoryForm(): 
    try:
        print('adding new category')
        data = json.loads(request.get_json())

        
        slug = data.get('category-slug')
        name = data.get('category-name')
        summary = data.get('category_summary')

        # this will be added to the dictionary with the key being the slug
        dictToAppend = {
            "title": name,
            "summary": summary,
            "subsections": []
        }
        
        regionKey = data.get('region_key')
        regionJson = load_json(regionKey + ".json")
        
        topicKey = data.get('topic_key')

        # Adds it to the data dict
        regionJson['topics'][topicKey]['categories'][slug] = dictToAppend


        # Saves the new json
        filepath = "data/" + regionKey + ".json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(regionJson, f, indent=2)


        global changesMade
        changesMade = True
        print('sucessfully added to form')
        return {"success": True}

    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}


@app.route('/addNewTopic', methods=['POST'])
@admin_required
def addTopicForm(): 
    try:
        print('adding new topic')
        data = json.loads(request.get_json())

        
        slug = data.get('topic-slug')
        name = data.get('topic-name')
        summary = data.get('topic_summary')
        # If its not checked, it wont show at all. If its checked it will show as 'true'
        addDefault = data.get("add_default_categories") == "true"

        # this will be added to the dictionary with the key being the slug
        dictToAppend = {
            "title": name,
            "description": summary,
            "categories": {}
        }

        # Adds some of the default categories to each topic
        if addDefault:
            dictToAppend['categories']['regulations'] = {
                "title": "Regulations",
                "description": "Overview of RF-related regulatory bodies and rules.",
                "subsections": []
            }
            dictToAppend["categories"]['testing'] = {
                "title": "Testing",
                "description": "Overview of RF testing requirements and procedures.",
                "subsections": []
            }
            dictToAppend['categories']['certifications'] = {
                "title": "Certifications",
                "description": "Overview of RF certification pathways.",
                "subsections": []
            }
            # dictToAppend['categories']['export-controls'] = {
            #     "title": "Export Controls",
            #     "description": "Overview of RF-related export and market-entry rules.",
            #     "subsections": []
            # }
            
        # Gets region data
        regionKey = data.get('region_key')
        regionJson = load_json(regionKey + ".json")
        
        # Adds it to the data dict
        regionJson['topics'][slug] = dictToAppend

        # Saves the new json
        filepath = "data/" + regionKey + ".json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(regionJson, f, indent=2)


        global changesMade
        changesMade = True
        print('sucessfully added to form')
        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}

@app.route('/addNewRegion', methods=['POST'])
@admin_required
def addNewRegion ():
    try:
        print('adding new region')
        data = json.loads(request.get_json())
        print('data')
        print(data)

        
        slug = data.get('region-slug')
        name = data.get('region-name')
        # If its not checked, it wont show at all. If its checked it will show as 'true'
        addDefault = data.get("add_default_topics") == "true"

        data = {
            "name": name,
            "topics": {}
        }

        # Adds the default data to topics
        if addDefault:
            data['topics'] = {
                "rf": {
                    "title": "Radio Frequency (RF)",
                    "description": "RF-related regulations, testing, certification, and export topics.",
                    "categories": {
                        "regulations": {
                            "title": "Regulations",
                            "description": "Overview of RF-related regulatory bodies and rules.",
                            "subsections": []
                        },
                        "testing": {
                            "title": "Testing",
                            "description": "Overview of RF testing requirements and procedures.",
                            "subsections": []
                        },
                        "certifications": {
                            "title": "Certifications",
                            "description": "Overview of RF certification pathways.",
                            "subsections": []
                        },
                        # "export-controls": {
                        #     "title": "Export Controls",
                        #     "description": "Overview of RF-related export and market-entry rules.",
                        #     "subsections": []
                        # }
                    }
                }, 
                "emc": {
                    "title": "Electromagnetic Compatibility (EMC)",
                    "description": "EMC-related regulations, testing, certification, and export topics.",
                    "categories": {
                        "regulations": {
                            "title": "Regulations",
                            "description": "Overview of EMC-related rules and standards.",
                            "subsections": []
                        },
                        "testing": {
                            "title": "Testing",
                            "description": "Overview of EMC testing requirements and procedures.",
                            "subsections": []
                        },
                        "certifications": {
                            "title": "Certifications",
                            "description": "Overview of EMC certification pathways.",
                            "subsections": []
                        },
                        # "export-controls": {
                        #     "title": "Export Controls",
                        #     "description": "Overview of EMC-related export and market-entry rules.",
                        #     "subsections": []
                        # }
                    }
                }, 
                "reliability": {
                    "title": "Reliability / Airworthiness",
                    "description": "Reliability, airworthiness, and safety-related topics.",
                    "categories": {
                        "regulations": {
                        "title": "Regulations",
                        "description": "Overview of reliability and airworthiness regulations.",
                        "subsections": []
                        },
                        "testing": {
                        "title": "Testing",
                        "description": "Overview of reliability and airworthiness testing procedures.",
                        "subsections": []
                        },
                        "certifications": {
                        "title": "Certifications",
                        "description": "Overview of reliability and airworthiness certification pathways.",
                        "subsections": []
                        },
                        # "export-controls": {
                        # "title": "Export Controls",
                        # "description": "Overview of reliability-related market-entry and export issues.",
                        # "subsections": []
                        # }
                    }
                },
                "Cybersecurity": {
                    "title": "Cybersecurity",
                    "description": "Cybersecurity Related Topics",
                    "categories": {
                        "regulations": {
                            "title": "Regulations",
                            "description": "Overview of cybersecurity regulations in Taiwan",
                            "subsections": []
                        },
                        "testing": {
                            "title": "Testing",
                            "description": "Overview of reliability and airworthiness testing procedures.",
                            "subsections": []
                        },
                        "certifications": {
                            "title": "Certifications",
                            "description": "Overview of reliability and airworthiness certification pathways.",
                            "subsections": []
                        },
                        # "export-controls": {
                        #     "title": "Export Controls",
                        #     "description": "Overview of reliability-related market-entry and export issues.",
                        #     "subsections": []
                        # }
                    }
                }
            }

        newFilepath = "data/" + slug + ".json"
        # Saves the data
        with open(newFilepath, "w") as f:
            json.dump(data, f)
        # commitAndPush()
        global changesMade
        changesMade = True
        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}

@app.route('/deleteEntry', methods=['POST'])
@admin_required
def deleteEntry():
    try:
        print('Deleting Entry')
        data = request.get_json()
        print('data')
        print(data)

        sourceTitle = data.get('sourceTitle')
        briefSummary = data.get('briefSummary')
        regionKey = data.get('regionKey')
        topicKey = data.get('topicKey')
        categoryKey = data.get('categoryKey')
        subsectionSlug = data.get('subsectionSlug')

        filePath = f"data/{regionKey}.json"
        # gets data for the 
        with open(filePath, "r", encoding="utf-8") as file:
            regionData = json.load(file)

        category = regionData["topics"][topicKey]["categories"][categoryKey]

        subsections = category["subsections"]
        subsectionIndex = getSubsectionIndexFromSlug(subsectionSlug, subsections)
        if subsectionIndex == -1:
            raise Exception('subsection not found from slug')
        
        entries = subsections[subsectionIndex].get("entries", [])


        for i, entry in enumerate(entries):
            if (entry.get("source_title") == sourceTitle and entry.get("brief_summary") == briefSummary):
                entries.pop(i)

                # Write updated JSON back to file
                with open(filePath, "w", encoding="utf-8") as file:
                    json.dump(regionData, file, indent=2)

                global changesMade
                changesMade = True
                print("Entry deleted")
                return {"success": True}

        raise Exception('entry not found...')
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}
    

@app.route('/deleteSubsection', methods=['POST'])
@admin_required
def deleteSubsection():
    try:
        print('Deleting Subsection')
        data = request.get_json()
        print('data')
        print(data)

        regionKey = data.get('regionKey')
        topicKey = data.get('topicKey')
        categoryKey = data.get('categoryKey')
        subsectionSlug = data.get('subsectionSlug')

        filePath = f"data/{regionKey}.json"

        with open(filePath, "r", encoding="utf-8") as file:
            regionData = json.load(file)

        category = regionData["topics"][topicKey]["categories"][categoryKey]

        subsections = category["subsections"]
        subsectionIndex = getSubsectionIndexFromSlug(subsectionSlug, subsections)
        if subsectionIndex == -1:
            raise Exception('subsection not found from slug')
        
        regionData["topics"][topicKey]["categories"][categoryKey]['subsections'].pop(subsectionIndex)

        with open(filePath, "w", encoding="utf-8") as file:
            json.dump(regionData, file, indent=2)
        global changesMade
        changesMade = True

        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}
    
@app.route('/editSubsection', methods=['POST'])
@admin_required
def editSubsection():
    try:
        print('Editing Subsection')
        data = request.get_json()
        print('data')
        print(data)

        regionKey = data.get('region_key')
        topicKey = data.get('topic_key')
        categoryKey = data.get('category_key')
        subsectionSlug = data.get('subsection_slug')
        newSubsectionSummary = data.get('newSubsectionSummary')
        newSubsectionName = data.get('newSubsectionName')

        filePath = f"data/{regionKey}.json"

        with open(filePath, "r", encoding="utf-8") as file:
            regionData = json.load(file)

        category = regionData["topics"][topicKey]["categories"][categoryKey]

        subsections = category["subsections"]
        subsectionIndex = getSubsectionIndexFromSlug(subsectionSlug, subsections)
        if subsectionIndex == -1:
            raise Exception('subsection not found from slug')
        
        regionData["topics"][topicKey]["categories"][categoryKey]['subsections'][subsectionIndex]['name'] = newSubsectionName
        regionData["topics"][topicKey]["categories"][categoryKey]['subsections'][subsectionIndex]['summary'] = newSubsectionSummary

        with open(filePath, "w", encoding="utf-8") as file:
            json.dump(regionData, file, indent=2)
        global changesMade
        changesMade = True

        return {"success": True}      
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}

@app.route('/deleteCategory', methods=['POST'])
@admin_required
def deleteCategory():
    try:
        print('Deleting Category')
        data = request.get_json()
        print('data')
        print(data)

        regionKey = data.get('regionKey')
        topicKey = data.get('topicKey')
        categoryKey = data.get('categoryKey')

        filePath = f"data/{regionKey}.json"

        with open(filePath, "r", encoding="utf-8") as file:
            regionData = json.load(file)

        regionData["topics"][topicKey]["categories"].pop(categoryKey)

        with open(filePath, "w", encoding="utf-8") as file:
            json.dump(regionData, file, indent=2)
        global changesMade
        changesMade = True

        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}

@app.route('/editCategory', methods=['POST'])
@admin_required
def editCategory():
    try:
        print('Editing Category')
        data = request.get_json()
        print('data')
        print(data)

        regionKey = data.get('region_key')
        topicKey = data.get('topic_key')
        categoryKey = data.get('category_key')
        newCategoryTitle = data.get('newCategoryTitle')
        newCategoryDescription = data.get('newCategoryDescription')

        filePath = f"data/{regionKey}.json"

        with open(filePath, "r", encoding="utf-8") as file:
            regionData = json.load(file)

        regionData["topics"][topicKey]["categories"][categoryKey]['title'] = newCategoryTitle
        regionData["topics"][topicKey]["categories"][categoryKey]['description'] = newCategoryDescription

        with open(filePath, "w", encoding="utf-8") as file:
            json.dump(regionData, file, indent=2)
        global changesMade
        changesMade = True

        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}
    
@app.route('/deleteTopic', methods=['POST'])
@admin_required
def deleteTopic():
    try:
        print('Deleting Topic')
        data = request.get_json()
        print('data')
        print(data)

        regionKey = data.get('regionKey')
        topicKey = data.get('topicKey')

        filePath = f"data/{regionKey}.json"

        with open(filePath, "r", encoding="utf-8") as file:
            regionData = json.load(file)

        regionData["topics"].pop(topicKey)

        with open(filePath, "w", encoding="utf-8") as file:
            json.dump(regionData, file, indent=2)
        global changesMade
        changesMade = True

        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}
    

@app.route('/editTopic', methods=['POST'])
@admin_required
def editTopic():
    try:
        print('Editing Topic')
        data = request.get_json()
        print('data')
        print(data)

        regionKey = data.get('region_key')
        topicKey = data.get('topic_key')
        newTopicTitle = data.get('newTopicTitle')
        newTopicDescription = data.get('newTopicDescription')

        filePath = f"data/{regionKey}.json"

        with open(filePath, "r", encoding="utf-8") as file:
            regionData = json.load(file)

        regionData["topics"][topicKey]['title'] = newTopicTitle
        regionData["topics"][topicKey]['description'] = newTopicDescription

        with open(filePath, "w", encoding="utf-8") as file:
            json.dump(regionData, file, indent=2)
        global changesMade
        changesMade = True

        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}

@app.route('/deleteRegion', methods=['POST'])
@admin_required
def deleteRegion():
    try:
        print('Deleting Region')
        data = request.get_json()
        print('data')
        print(data)

        regionKey = data.get('regionKey')

        filePath = f"data/{regionKey}.json"

        if not os.path.exists(filePath):
            raise Exception('region file not found')

        os.remove(filePath)

        global changesMade
        changesMade = True
        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}
    
@app.route('/editRegion', methods=['POST'])
@admin_required
def editRegion():
    try:
        print('Editing Region')
        data = request.get_json()
        print('data')
        print(data)

        regionKey = data.get('region_key')
        newRegionName = data.get('newRegionName')

        filePath = f"data/{regionKey}.json"

        with open(filePath, "r", encoding="utf-8") as file:
            regionData = json.load(file)

        regionData['name'] = newRegionName

        with open(filePath, "w", encoding="utf-8") as file:
            json.dump(regionData, file, indent=2)
        global changesMade
        changesMade = True

        return {"success": True}
    except Exception as e:
        print('ERROR SUBMITTING FORM')
        print(e)
        return {"success": False}

if __name__ == "__main__":
    app.run()