import os
import json


def loadJsonFromFilepath (filePath: str):
    with open(filePath, "r", encoding="utf-8") as f:
        return json.load(f)

# Reads all the json files and makes a list of dicts that have all the data:
def getDataFromRegions (regions = []):
    # List of all json files in data
    jsonFileNames = os.listdir('./data')
    
    data = []
    for fileName in jsonFileNames:
        regionShorthand = fileName[0:-5] # the region name with no json
        if len(regions) == 0 or regionShorthand in regions:
            fileData = loadJsonFromFilepath("./data/" + fileName)
            fileData['fileName'] = fileName # adds this extra information
            data.append(fileData)

    return data

# print(getData())

def keywordSearch (keyword, regions = []):
    keyword = keyword.lower()

    data = getDataFromRegions(regions) # Dict with all json data
    results = [] # Output Array

    # Each path will be a python object that has a standarized way to uniqly identify each page 
    # In this form:
    """
    resultDict = {
        # Used for finding the article later (index)
        'path': '/region/eu/rf/regulations',
        'title': 'Regulations',
        'text': 'Overview of RF-related regulatory bodies and rules.',
        'sortLevel': '', # Used to sort the list to make regions and subsections go to the top
        'type': 'category'
    }
    """
    for countryDict in data:
        fileName = countryDict.get('fileName')
        fileShorthand = fileName[0:-5] # strips out the .json from the file name
        regionName = countryDict.get('name')
        topics = countryDict.get('topics', {})
                # Appends the region's page into the list if it matches

        if keyword in regionName.lower():
            pagePath = '/region/' + fileShorthand
            resultDict = {
                'path': pagePath,
                'title': regionName,
                'text': '',
                'sortLevel': 0,
                'type': 'region'
            }
            results.append(resultDict)

        for topicName, topicDict in topics.items():
            topicTitle = topicDict.get('title', '')
            topicDescription = topicDict.get('description', '')
            categories = topicDict.get('categories', {})

            # Checks to see if the topic page should be added:
            if keyword in topicTitle.lower() or keyword in topicDescription.lower():
                sortLevel = 2
                # If the keyword is in the title of the topic, we want to show that first
                if keyword in topicTitle.lower():
                    sortLevel = 1

                pagePath = '/region/' + fileShorthand + '/topic/' + topicName
                resultDict = {
                    'path': pagePath,
                    'title': topicTitle,
                    'text': topicDescription,
                    'sortLevel': sortLevel,
                    'type': 'category'
                }
                results.append(resultDict)

            for categoryName, categoryDict in categories.items():
                categoryTitle = categoryDict.get('title', '')
                categoryDescription = categoryDict.get('description', '')

                # Checks to see if the category page should be added:
                if keyword in categoryTitle.lower() or keyword in categoryDescription.lower():
                    sortLevel = 3
                    # If the keyword is in the title of the category, we want to show that first
                    if keyword in categoryTitle.lower():
                        sortLevel = 1.1

                    pagePath = '/region/' + fileShorthand + '/topic/' + topicName + '/category/' + categoryName
                    resultDict = {
                        'path': pagePath,
                        'title': categoryTitle,
                        'text': categoryDescription,
                        'sortLevel': sortLevel,
                        'type': 'subsection'
                    }
                    results.append(resultDict)

                subsections = categoryDict.get('subsections', [])
                for subsection in subsections:
                    subsectionTitle = subsection.get('name', '')
                    subsectionSummary = subsection.get('summary', '')
                    subsectionSlug = subsection.get('slug', '')

                    # Once again tests to see if the keyword is found in the subsection name or description:
                    if keyword in subsectionTitle.lower() or keyword in subsectionSummary.lower():
                        sortLevel = 4
                        # If the keyword is in the title of the subsection, we want to show that first
                        if keyword in subsectionTitle.lower():
                            sortLevel = 1.2

                        pagePath = '/region/' + fileShorthand + '/topic/' + topicName + '/category/' + categoryName + '/subsection/' + subsectionSlug
                        resultDict = {
                            'path': pagePath,
                            'title': subsectionTitle,
                            'text': subsectionSummary,
                            'sortLevel': sortLevel,
                            'type': 'subsection'
                        }
                        results.append(resultDict)

                    entryIndex = 0

                    entries = subsection.get('entries')
                    if entries is None:
                        entryIndex += 1
                        continue

                    for entry in entries:
                        entrySummary = entry.get('brief_summary', '')
                        entryTitle = entry.get('source_title', '')

                        if keyword in entryTitle.lower() or keyword in entrySummary.lower():
                            sortLevel = 5
                            # If the keyword is in the title of the entry, we want to show that first
                            if keyword in entryTitle.lower():
                                sortLevel = 1.3

                            pagePath = '/region/' + fileShorthand + '/topic/' + topicName + '/category/' + categoryName + '/subsection/' + subsectionSlug + '?index=' + str(entryIndex)
                            resultDict = {
                                'path': pagePath,
                                'title': entryTitle,
                                'text': entrySummary,
                                'sortLevel': sortLevel,
                                'type': 'entry'
                            }
                            results.append(resultDict)

                    entryIndex += 1

        
    sortedResults = sorted(results, key=lambda x: x.get("sortLevel", 0))
    return sortedResults

# This is old and works with the old json format. DO NOT USE:
def keywordSearchOLD (keyword, regions = []):
    keyword = keyword.lower()

    data = getDataFromRegions(regions)
    results = []

    # Each path will be a python object that has a standarized way to uniqly identify each page 
    # In this form:
    """
    resultDict = {
        # Used for finding the article later (index)
        'path': '/region/taiwan',
        'title': 'European Union 欧洲联盟', # Title of what is used to get ther 
        'text': '',
        'sortLevel': '', # Used to sort the list to make regions and subsections go to the top
        'type': 'region'
    }
    """
    # This is a simple way to uniqly identify any article in the current system. 
    # displayText & region are used for displaying search results

    for countryDict in data:
        fileName = countryDict.get('fileName')
        fileShorthand = fileName[0:-5] #strips out the .json from the file name
        categories = countryDict.get('categories') # list of catagories (each is a dict)
        # ^ dictionary with catagory name keys

        regionName = countryDict.get('name')

        # Appends the region's page into the list if it matches
        if keyword in regionName.lower():
            # print('FOUND REGION: ', regionName, "   ", fileShorthand)
            pagePath = '/region/' + fileShorthand
            resultDict = {
                # Used for finding the article later (index)
                'path': pagePath,
                'title': regionName,
                'text': '',
                'sortLevel': 0,
                'type': 'region'
            }
            results.append(resultDict)

        for categoryName, categoryDict in categories.items():

            # Checks to see if the category page should be added:
            categoryDescription = categoryDict.get('description')
            categoryTitle = categoryDict.get('title') # This is what is on the 'title' in the json - used for display
            # If the keyword is in the category desciption or title
            if keyword in categoryDescription.lower() or keyword in categoryTitle.lower():
                sortLevel = 2
                # If the keyword is in the title of the catogory, we want to show that first (sort level lower) - becuase it wont be bolded later on
                if keyword in categoryTitle.lower():
                    sortLevel = 1

                # print('FOUND Category: ', categoryTitle)
                pagePath = '/region/' + fileShorthand + '/' + categoryName
                resultDict = {
                    # Used for finding the article later (index)
                    'path': pagePath,
                    'title': categoryTitle,
                    'text': categoryDescription,
                    'sortLevel': sortLevel,
                    'type': 'category'
                }
                results.append(resultDict)


            subsections = categoryDict.get('subsections')
            subsectionIndex = 0
            for subsection in subsections:
                # print('\n')
                # print(subsection.get('slug'))
                # print(subsection)

                subsectionTitle = subsection.get('name')
                subsectionSummary = subsection.get('summary')
                subsectionSlug = subsection.get('slug')
                # Once again tests to see if the keyword is found in the subsection name or description:
                if keyword in subsectionTitle.lower() or keyword in subsectionSummary.lower():
                    sortLevel = 3
                    # If the keyword is in the title of the subsection, we want to show that first (sort level lower) - becuase it wont be bolded later on
                    if keyword in categoryTitle.lower():
                        sortLevel = 1.1

                    pagePath = '/region/' + fileShorthand + '/' + categoryName + '/' + subsectionSlug
                    resultDict = {
                        # Used for finding the article later (index)
                        'path': pagePath,
                        'title': subsectionTitle,
                        'text': subsectionSummary,
                        'sortLevel': sortLevel,
                        'type': 'subsection'
                    }


                entries = subsection.get('entries')
                if entries is None: 
                    subsectionIndex += 1 
                    continue

                for entry in entries:
                    
                    entrySummary = entry.get('brief_summary')
                    entryTitle = entry.get('source_title')

                    if keyword in entryTitle.lower():
                        sortLevel = 4
                        # If the keyword is in the title of the entry, we want to show that first (sort level lower) - becuase it wont be bolded later on
                        if keyword in categoryTitle.lower():
                            sortLevel = 1.2

                        pagePath = '/region/' + fileShorthand + '/' + categoryName + '/' + subsectionSlug + '?index=' + str(subsectionIndex)
                        resultDict = {
                            # Used for finding the article later (index)
                            'path': pagePath,
                            'title': entryTitle,
                            'text': entrySummary,
                            'sortLevel': sortLevel,
                            'type': 'entry'
                        }
                        results.append(resultDict)
                
                subsectionIndex += 1 
        
    sortedResults = sorted(results, key=lambda x: x.get("sortLevel", 0))
    
    return sortedResults

if __name__ == '__main__':
    print('TYPE YOUR SEARCH HERE: ')
    res = keywordSearch(input())

    if len(res) == 0:
        print("NO RESULTS FOUND")

    for result in res:
        print("="*80)
        print('RESULT: ')
        print(result)
        finalLink = 'http://127.0.0.1:5000' + result.get('path')
        print(finalLink)