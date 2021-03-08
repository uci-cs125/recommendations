from app.utils.db import mongoClient
import requests
import os
import json
import random
import pymongo


recipes_collection = mongoClient["recommendations"]["recipes"]
liked_collection = mongoClient["recommendations"]["likes"]
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
                result = recipes_collection.find_one({"id": recipe['id']})
                recipeID = recipe['id']

                if result == None:
                    print(f'recipe not found in DB: {recipeID}, appending...')
                    insertResult = recipes_collection.insert_one(recipe)
                    print(f'Inserted recipe: {recipeID}')
            offset = offset+100

    def populateRecipeFields(self):
        res = recipes_collection.find({"tags": None}, batch_size=20000, cursor_type=pymongo.cursor.CursorType.EXHAUST)
        print("got recipes")
        recipes = [r for r in res]
        print("got array")

        for recipe in recipes:
            # self._populateTasteFieldForRecipe(recipe)
            # print("populating tags field for recipe:")
            self._populateTagsFieldForRecipe(recipe)
            # self._fixFields(recipe)
            # self._populateNutritionFieldsForRecipe(recipe)
            # print("Finished populating all fields for recipe: ", recipe['id'])

    def _populateTagsFieldForRecipe(self, recipe):
        recipeTags = []
        for tag in recipe['diets']:
            recipeTags.append(tag)
        for tag in recipe['cuisines']:
            recipeTags.append(tag)
        for tag in recipe['dishTypes']:
            recipeTags.append(tag)
        for tag in recipe['occasions']:
            recipeTags.append(tag)
        if recipe['veryHealthy']:
            recipeTags.append('veryHealthy')
        if recipe['sustainable']:
            recipeTags.append('sustainable')
        if recipe['cheap']:
            recipeTags.append('cheap')

        res = recipes_collection.update({'id': recipe['id']}, { 
            '$set': {
                "tags": recipeTags
            }
        })
        # print("UPDATE res:", res)

    def _populateTasteFieldForRecipe(self, recipe):
            r = requests.get(f'https://api.spoonacular.com/recipes/{recipe["id"]}/tasteWidget.json/?apiKey={self.apiToken}')
            resp = r.json()
            
            res = recipes_collection.update({'id': recipe['id']}, { 
                    '$set': {
                        "tasteProfile": resp
                    }
                })
            # print("UPDATED taste field for recipe:", recipe['id'], res)

    def _populateNutritionFieldsForRecipe(self, recipe):
        r = recipes_collection.find({ "id": recipe['id'], "calories": { "$exists": True} })
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
            res = recipes_collection.update({'id': recipe['id']}, payload)





dbPopulator = DatabasePopulator("31badbba838549c59b1ca8f72c92d501")
# dbPopulator.populateRecipes()
# dbPopulator.populateRecipeFields()
