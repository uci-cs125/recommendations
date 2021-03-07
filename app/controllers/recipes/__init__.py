from app.utils.db import mongoClient
import requests
import os
import json
import random


recipesCollection = mongoClient["recommendations"]["recipes"]
likedCollection = mongoClient["recommendations"]["likes"]
class CamelCasify:
    def camelify(self, words):
        s = "".join(word[0].upper() + word[1:].lower() for word in words)
        return s[0].lower() + s[1:]
camelifier = CamelCasify()


class DatabasePopulator:
    def __init__(self, apiToken):
        self.apiToken = apiToken    # instance variable

    def populateRecipes(self):
        offset = 0
        for i in range(0, 1000):
            print(f'Offset: {offset}')

            r = requests.get(f'https://api.spoonacular.com/recipes/complexSearch/?apiKey={self.apiToken}&addRecipeNutrition=true&addRecipeInformation=true&number=100&offset={offset}&sort=random')
            resp = r.json()
            # print(resp)
            for recipe in resp['results']:
                result = recipesCollection.find_one({"id": recipe['id']})
                recipeID = recipe['id']

                if result == None:
                    print(f'recipe not found in DB: {recipeID}, appending...')
                    insertResult = recipesCollection.insert_one(recipe)
                    print(f'Inserted recipe: {recipeID}')
            offset = offset+100

    def populateRecipeFields(self):
        result = recipesCollection.find({"netCarbohydrates": None}) # only get records that are missing the field, makes this endpoint idempotent.
        recipes = [r for r in result]
        print("Populating taste fields...")

        for recipe in recipes:
            # self._populateTasteFieldForRecipe(recipe)
            self._fixFields(recipe)
            # self._populateNutritionFieldsForRecipe(recipe)
            print("Finished populating all fields for recipe: ", recipe['id'])


    def _populateTasteFieldForRecipe(self, recipe):
            r = requests.get(f'https://api.spoonacular.com/recipes/{recipe["id"]}/tasteWidget.json/?apiKey={self.apiToken}')
            resp = r.json()
            
            res = recipesCollection.update({'id': recipe['id']}, { 
                    '$set': {
                        "tasteProfile": resp
                    }
                })
            print("UPDATED taste field for recipe:", recipe['id'], res)

    def _fixFields(self, recipe):
        r = requests.get(f'https://api.spoonacular.com/recipes/{recipe["id"]}/information/?apiKey={self.apiToken}&includeNutrition=true')
        resp = r.json()
        # print("resp:", resp)

        carbs = resp['nutrition']['nutrients'][3]
        netCarbs = resp['nutrition']['nutrients'][4]
        print("Carbs: ", carbs)
        print("net carbs:", netCarbs)
        res = recipesCollection.update({'id': recipe['id']}, { 
                '$set': {
                    "netCarbohydrates": netCarbs,
                    "carbohydrates": carbs,
                }
            })
        
    def _populateNutritionFieldsForRecipe(self, recipe):
        r = recipesCollection.find({ "id": recipe['id'], "calories": { "$exists": True} })
        if len(list(r)) == 0:
            print(f'Document with recipe.id = {recipe["id"]} already contains calories field')
            return

        calories = { 'name': "Calories", "units": "kcal", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'calories'}
        fat = { 'name': "Fat", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'fat'}
        saturatedFat = { 'name': "Saturated Fat", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'saturatedFat'}
        cholesterol = { 'name': "Cholesterol", "units": "mg", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'cholesterol'}
        sodium = { 'name': "Sodium", "units": "mg", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'sodium'}
        netCarbs = { 'name': "Net Carbohydrates", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'netCarbohydrates'}
        carbs = { 'name': "Carbohydrates", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'netCarbohydrates'}
        fiber = { 'name': "Fiber", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'fiber'}
        sugar = { 'name': "Sugar", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'sugar'}
        protein = { 'name': "Protein", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'protein'}

        for nutrient in recipe["nutrition"]["nutrients"]:
            nutrientName = nutrient['name'].lower()
            nutrientName = camelifier.camelify(nutrientName.split(" "))
        
            nutrient['shortName'] = nutrientName
            if nutrient['name'] == 'Calories':
                calories = nutrient
            if nutrient['name'] == 'Fat':
                fat = nutrient
            if nutrient['name'] == 'Saturated Fat':
                saturatedFat = nutrient
            if nutrient['name'] == 'Cholesterol':
                cholesterol = nutrient
            if nutrient['name'] == 'Sodium':
                sodium = nutrient
            if nutrient['name'] == 'Net Carbohydrates':
                netCarbs = nutrient
            if nutrient['name'] == 'Carbohydrates':
                carbs = nutrient
            if nutrient['name'] == 'Fiber':
                fiber = nutrient
            if nutrient['name'] == 'Sugar':
                sugar = nutrient
            if nutrient['name'] == 'Protein':
                protein = nutrient

        nutrients = [calories, fat, saturatedFat, cholesterol, sodium, netCarbs, fiber, sugar, protein]
        for nutrient in nutrients:
            shortName = nutrient['shortName']
            payload = { 
                    '$set': {
                        shortName: nutrient
                    }
                }
            res = recipesCollection.update({'id': recipe['id']}, payload)


dbPopulator = DatabasePopulator("31badbba838549c59b1ca8f72c92d501")
# dbPopulator.populateRecipes()

dbPopulator.populateRecipeFields()
