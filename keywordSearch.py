import os
import json


def loadJsonFromFilepath (filePath: str):
    with open(filePath, "r", encoding="utf-8") as f:
        return json.load(f)

# Reads all the json files and makes a list of dicts that have all the data:
def getData ():
    # List of all json files in data
    jsonFileNames = os.listdir('./data')
    
    data = []
    for fileName in jsonFileNames:
        fileData = loadJsonFromFilepath("./data/" + fileName)
        fileData['fileName'] = fileName # adds this extra information
        data.append(fileData)

    return data

# print(getData())

# Main function to use:
def keywordSearch (keyword):
    keyword = keyword.lower()

    data = getData()
    results = []

    # Each path will be a python object that has a standarized way to uniqly identify each article 
    # In this form:
    """
    resultDict = {
        # Used for finding the article later (index)
        'fileName': 'EU.json',
        'categoryName': 'regulations',
        'subsectionIndex': 0,

        # Used for displaying search results
        'displayText': '...100 chacters around the keyword...',
        'region': 'European Union',
        'primary_category': 'Reliability / Airworthiness',
        'secondary_category': 'Misc / Context',
        'subsection_slug': 'easa',
        'topic': 'EU foundational drone regulations',
        'summary': 'Bundle notes summarizing the EU legal foundation for manufacturer and operator regulation.'
    }
    """
    # This is a simple way to uniqly identify any article in the current system. 
    # displayText & region are used for displaying search results

    for countryDict in data:
        fileName = countryDict.get('fileName')
        categories = countryDict.get('categories') # list of catagories (each is a dict)
        # ^ dictionary with catagory name keys

        for categoryName, categoryDict in categories.items():
            # print('='*80)
            # print('categoryName')
            # print(categoryName)
            subsections = categoryDict.get('subsections')
            subsectionIndex = 0
            for subsection in subsections:
                # print('\n')
                # print(subsection.get('slug'))
                # print(subsection)


                entries = subsection.get('entries')
                if entries is None: 
                    subsectionIndex += 1 
                    continue

                for entry in entries:
                    
                    summary = entry.get('brief_summary')

                    if keyword in summary.lower():
                        resultDict = {
                            # Used for finding the article later (index)
                            'fileName': fileName,
                            'categoryName': categoryName,
                            'subsectionIndex': subsectionIndex,

                            # Used for displaying search results 
                            # 'displayText': '...100 chacters around the keyword...',
                            #'region': 'European Union',
                            #'primary_category': 'Reliability / Airworthiness',
                            #'secondary_category': 'Misc / Context',
                            #'subsection_slug': 'easa',
                            #'topic': 'EU foundational drone regulations',
                            'summary': summary
                        }
                        results.append(resultDict)
                
                subsectionIndex += 1 
        
        # for categoryDict in countryDict['categories']:
            # categoryName = categoryDict[]


    return results


print('TYPE YOUR SEARCH HERE: ')
res = keywordSearch(input())

if len(res) == 0:
    print("NO RESULTS FOUND")

for result in res:
    print("="*80)
    print('RESULT: ')
    print(result)