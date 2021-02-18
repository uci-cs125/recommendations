from app.utils.db import mongoClient
import requests
import os

recipesCollection = mongoClient["recommendations"]["recipes_filtered_for_lauras_shitty_laptop"]#["recipes"]
likedCollection = mongoClient["recommendations"]["likes"]

def populateTasteVectorField():
    API_TOKEN = "31badbba838549c59b1ca8f72c92d501"
    headers = {'Authorization': 'Bearer ' + API_TOKEN}

    result = recipesCollection.aggregate([{
            '$project': {
                'id': 1
                }
            }
        ])
    recipes = [r for r in result]

    for recipe in recipes:
        print("getting taste profile for recipe:", recipe)
        url = 'https://api.spoonacular.com/recipes/' + str(recipe['id']) + '/tasteWidget.json' + '?apiKey=' + API_TOKEN
        print('url:', url)
        r = requests.get(url = url, headers = headers)
        if r.status_code != 200:
            print("Skipping unsuccessful status code:", r.status_code)
            continue
        print(r.json())
        recipesCollection.update({
                'id': recipe['id']
            },
            { 
                '$set': {
                    'tasteProfile': r.json(),
                }
            }
        )
# populateTasteVectorField()