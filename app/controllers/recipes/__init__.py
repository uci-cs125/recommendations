from app.utils.db import mongoClient
import requests
import os
import json

recipesCollection = mongoClient["recommendations"]["recipes"]
likedCollection = mongoClient["recommendations"]["likes"]
class CamelCasify:
   def camelify(self, words):
      s = "".join(word[0].upper() + word[1:].lower() for word in words)
      return s[0].lower() + s[1:]
camelifier = CamelCasify()

# def populateField():
#     API_TOKEN = "31badbba838549c59b1ca8f72c92d501"
#     headers = {'Authorization': 'Bearer ' + API_TOKEN}
#     print("finding recipes")
#     result = recipesCollection.find({})
#     recipes = [r for r in result]

#     # fat, saturated fat, cholesterol, sodium, carbohydrates, dietary fiber, sugar, protein, ca
#     # units, percent daily value for each
#     nutrientsExtracted = {}
#     for recipe in recipes:
#         print("recipe:", recipe)
#         for nutrient in recipe["nutrition"]["nutrients"]:
#             nutrientName = nutrient['name'].lower()
#             nutrientName = camelifier.camelify(nutrientName.split(" "))
            
#             addToCollection = False
#             if nutrient['name'] == 'Calories':
#                 addToCollection = True
#             if nutrient['name'] == 'Fat':
#                 addToCollection = True
#             if nutrient['name'] == 'Saturated Fat':
#                 addToCollection = True
#             if nutrient['name'] == 'Cholesterol':
#                 addToCollection = True
#             if nutrient['name'] == 'Sodium':
#                 addToCollection = True
#             if nutrient['name'] == 'Carbohydrates':
#                 addToCollection = True
#             if nutrient['name'] == 'Dietary Fiber':
#                 addToCollection = True
#             if nutrient['name'] == 'Sugar':
#                 addToCollection = True
#             if nutrient['name'] == 'Protein':
#                 addToCollection = True

#             if addToCollection:
#                 payload = { 
#                         '$set': {
#                             nutrientName: nutrient
#                         }
#                     }
#                 res = recipesCollection.update({'id': recipe['id']}, payload)
#                 print("UPDATED RECIPE ID: ", recipe['id'])
#                 print("RESULT:", res)
#         os.exit()
# populateField()