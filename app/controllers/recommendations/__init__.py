from app.utils.db import mongoClient
import requests
## Set up the recommendations database connection
recsClient = mongoClient.recommendations["recommendations"]



# Spoonacular Data Ingestion
def ingestData():
    API_TOKEN = "31badbba838549c59b1ca8f72c92d501"

    recipesClient = mongoClient.recipes["recipes"]
    recipe_id = 716430
    for i in range(0, 2):
        url = 'https://api.spoonacular.com/recipes/' + str(recipe_id) + '/information?apiKey=' + API_TOKEN + '&includeNutrition=true'
        headers = {'Authorization': 'Bearer ' + API_TOKEN}

        r = requests.get(url = url, headers = headers)
        if r.status_code != 200:
            print("Skipping unsuccessful status code:", r.status_code)
            continue

        print("Ingesting data: ",r.json())
        recipesClient.insert_one(r.json())
        recipe_id = recipe_id+1

# ingestData() 
