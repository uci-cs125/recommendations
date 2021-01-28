import pymongo
import requests
from app.utils.db import mongoClient

## Set up the users database connection and ensure the username field is indexed uniquely
usersClient = mongoClient.users["users"]
usersClient.create_index(
    [("username", pymongo.DESCENDING)],
    unique=True
)

authClient = mongoClient.users["authStore"]

API_TOKEN = "31badbba838549c59b1ca8f72c92d501"



def ingestData():
    recipesClient = mongoClient.recipes["recipes"]
    recipe_id = 716430
    for i in range(0, 100):
        url = 'https://api.spoonacular.com/recipes/' + str(recipe_id) + '/information?apiKey=' + API_TOKEN + '&includeNutrition=true'
        headers = {'Authorization': 'Bearer ' + API_TOKEN}

        r = requests.get(url = url, headers = headers)
        if r.status_code != 200:
            continue

        print("Ingesting data: ",r.json())
        recipesClient.insert_one(r.json())
        recipe_id = recipe_id+1

ingestData()