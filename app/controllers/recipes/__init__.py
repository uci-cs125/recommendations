from app.utils.db import mongoClient
import requests
import os
import json

recipesCollection = mongoClient["recommendations"]["recipes"]
likedCollection = mongoClient["recommendations"]["likes"]
# class CamelCasify:
#    def camelify(self, words):
#       s = "".join(word[0].upper() + word[1:].lower() for word in words)
#       return s[0].lower() + s[1:]
# camelifier = CamelCasify()

# def populateField():
#     API_TOKEN = "31badbba838549c59b1ca8f72c92d501"
#     headers = {'Authorization': 'Bearer ' + API_TOKEN}
#     print("finding recipes")
#     result = recipesCollection.find({})
#     recipes = [r for r in result]

#     # fat, saturated fat, cholesterol, sodium, carbohydrates, dietary fiber, sugar, protein, ca
#     # units, percent daily value for each

#     for recipe in recipes:
#         # calories = { 'name': "Calories", "units": "kcal", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'calories'}
#         # fat = { 'name': "Fat", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'fat'}
#         # saturatedFat = { 'name': "Saturated Fat", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'saturatedFat'}
#         # cholesterol = { 'name': "Cholesterol", "units": "mg", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'cholesterol'}
#         # sodium = { 'name': "Sodium", "units": "mg", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'sodium'}
#         # netCarbs = { 'name': "Net Carbohydrates", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'netCarbs'}
#         carbs = { 'name': "Carbohydrates", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'carbs'}
#         # fiber = { 'name': "Fiber", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'fiber'}
#         # sugar = { 'name': "Sugar", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'sugar'}
#         # protein = { 'name': "Protein", "units": "g", "percentOfDailyNeeds": 0.0, 'amount': 0.0, 'shortName': 'protein'}
#         for nutrient in recipe["nutrition"]["nutrients"]:
#             nutrientName = nutrient['name'].lower()
#             nutrientName = camelifier.camelify(nutrientName.split(" "))
        
#             nutrient['shortName'] = nutrientName
#             if nutrient['name'] == 'Calories':
#                 calories = nutrient
#             if nutrient['name'] == 'Fat':
#                 fat = nutrient
#             if nutrient['name'] == 'Saturated Fat':
#                 saturatedFat = nutrient
#             if nutrient['name'] == 'Cholesterol':
#                 cholesterol = nutrient
#             if nutrient['name'] == 'Sodium':
#                 sodium = nutrient
#             if nutrient['name'] == 'Net Carbohydrates':
#                 netCarbs = nutrient
#             if nutrient['name'] == 'Carbohydrates':
#                 carbs = nutrient
#                 break
#             if nutrient['name'] == 'Fiber':
#                 fiber = nutrient
#             if nutrient['name'] == 'Sugar':
#                 sugar = nutrient
#             if nutrient['name'] == 'Protein':
#                 protein = nutrient

#         nutrients = [carbs]
#         # nutrients = [calories, fat, saturatedFat, cholesterol, sodium, netCarbs, fiber, sugar, protein]
#         for nutrient in nutrients:
#             shortName = nutrient['shortName']
#             payload = { 
#                     '$set': {
#                         shortName: nutrient
#                     }
#                 }
#             print("payload:", payload)
#             res = recipesCollection.update({'id': recipe['id']}, payload)
#             print("UPDATED RECIPE ID: ", recipe['id'])
# populateField()