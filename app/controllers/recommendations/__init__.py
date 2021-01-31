from app.utils.db import mongoClient
import requests
import os

recsCollection = mongoClient["recommendations-" + os.getenv("ENVIRONMENT", "dev")]["recommendations"]
print("recsCollection:", recsCollection)
# Spoonacular Data Ingestion
def ingestData():
    API_TOKEN = "31badbba838549c59b1ca8f72c92d501"

    recipe_id = 716430
    for i in range(0, 1):
        url = 'https://api.spoonacular.com/recipes/' + str(recipe_id) + '/information?apiKey=' + API_TOKEN + '&includeNutrition=true'
        headers = {'Authorization': 'Bearer ' + API_TOKEN}

        r = requests.get(url = url, headers = headers)
        if r.status_code != 200:
            print("Skipping unsuccessful status code:", r.status_code)
            continue

        print("Ingesting data: ",r.json())
        recsCollection.insert_one(r.json())
        recipe_id = recipe_id+1

# ingestData() 
