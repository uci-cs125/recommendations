from app.utils.db import mongoClient
import requests
import os

recipesCollection = mongoClient["recommendations"]["recipes"]

# Spoonacular Data Ingestion
# def ingestData():
#     API_TOKEN = "31badbba838549c59b1ca8f72c92d501"
#     headers = {'Authorization': 'Bearer ' + API_TOKEN}

#     offset = 0
#     for i in range(0, 11):
#         url = 'https://api.spoonacular.com/recipes/complexSearch?includeNutrition=true&number=1000&fillIngredients=true&addRecipeInformation=true&addRecipeNutrition=true&fillIngredients=true&includeNutrition=true&number=100&offset=' + str(offset) + '&apiKey=' + API_TOKEN
#         print("url:", url)
#         r = requests.get(url = url, headers = headers)
#         if r.status_code != 200:
#             print("Skipping unsuccessful status code:", r.status_code)
#             continue

#         offset = offset + 100 ### 100 results at a time, store them all in the mongo DB, then increment to the next 100 results :D
#         result = recsCollection.insert_many(r.json()['results'])
#         print("Result:", result)

# ingestData() 
