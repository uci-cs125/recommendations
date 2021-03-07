
import requests
from . import recipesCollection
from . import likedCollection
from scipy import spatial
import threading
import time

class QueryEngine():
    def __init__(self):
        # fetch the list of all recipes one time during startup to reduce query time
        print("fetching recipes...")
        allRecipes = recipesCollection.find({})
        self.recipes = [doc for doc in allRecipes]
        print("finished fetching recipes, ready to accept queries.")

    def query(self, payload):
        print(f'received query payload: {payload}')
        profile = payload["profile"]
        context = payload["context"]

        # result = recipesCollection.
        #     # { 
        #     #     '$match': { 
        #     #         'dishTypes': { 
        #     #             '$all': [mealType]
        #     #         }
        #     #     }
        #     # }, 
        rankedRecipes = self._assemble_rankings(profile["uid"], self.recipes, payload)
        print
        sortedRecipes = sorted(rankedRecipes, 
                                key = lambda i: i['tagScore'],
                                reverse=True)
        # recommendations = sorted(self.recipes, \
        #                         key = lambda i: i['nutritionalScore']*.5 + \
        #                                         i['tasteScore']*.5, \
        #                         reverse=True)
        # print("First recommendation: ", recommendations[0]['id'], " with score of: ", recommendations[0]['nutritionalScore']*.5+recommendations[0]['tasteScore']*.5)
        return sortedRecipes[:50]

    def _getLikesByUserId(self, user_id):
        result = likedCollection.find({'user_id': user_id})
        likes = [like for like in result]
        if len(likes) == 0:
            print("User does not have any likes:", user_id)
            return None

        print('returning likes list:', likes)
        return likes

    def _get_recipes_liked_vector(self, likes):
        total_sweetness, total_saltiness, total_sourness, total_bitterness, \
        total_savoriness, total_fattiness, total_spiciness = 0,0,0,0,0,0,0
        for like in likes:
            likedRecipe = recipesCollection.find_one({'id': like['recipe_id']})
            if likedRecipe == None:
                print("User liked a Recipe that does not exist!", like['recipe_id'])
                continue

            tasteProfile = likedRecipe["tasteProfile"]
            total_sweetness += tasteProfile["sweetness"]
            total_saltiness += tasteProfile["saltiness"]
            total_sourness += tasteProfile["sourness"]
            total_bitterness += tasteProfile["bitterness"]
            total_savoriness += tasteProfile["savoriness"]
            total_fattiness += tasteProfile["fattiness"]
            total_spiciness += tasteProfile["spiciness"]

        # return average taste vector     
        return [
            total_sweetness/len(likes), 
            total_saltiness/len(likes), 
            total_sourness/len(likes), 
            total_bitterness/len(likes), 
            total_savoriness/len(likes), 
            total_fattiness/len(likes), 
            total_spiciness/len(likes)
        ]
    def _compute_scores(self, recipes, likes, tagFreqs, query_payload):

        recipes_liked_vector = self._get_recipes_liked_vector(likes)
        for index, recipe in enumerate(recipes):

            # print(f'Computing tag score for recipe {recipe["id"]}')
            ###### COMPUTE TAG SCORE ######
            recipeTags = {}
            for tag in recipe['diets']:
                recipeTags[tag] = True
            for tag in recipe['cuisines']:
                recipeTags[tag] = True
            for tag in recipe['dishTypes']:
                recipeTags[tag] = True
            for tag in recipe['occasions']:
                recipeTags[tag] = True
            if recipe['veryHealthy']:
                recipeTags['veryHealthy'] = True
            if recipe['sustainable']:
                recipeTags['sustainable'] = True
            if recipe['cheap']:
                recipeTags['cheap'] = True

            totalLikeFrequencies = 0
            recipeTagScore = 0
            for tag in tagFreqs:
                totalLikeFrequencies += tagFreqs[tag]
            for tag in tagFreqs:
                if tag in recipeTags:
                    recipeTagScore += (tagFreqs[tag]/totalLikeFrequencies)
            recipes[index]['tagScore'] = recipeTagScore

            # print(f'Computing taste score for recipe {recipe["id"]}')
            ### COMPUTE TASTE SCORE
            recipe_profile = recipe['tasteProfile']
            recipe_vector = [recipe_profile['sweetness'], recipe_profile['saltiness'], recipe_profile['sourness'], 
                                recipe_profile['bitterness'], recipe_profile['savoriness'], recipe_profile['fattiness'], 
                                recipe_profile['spiciness']]
            print(f'computed query vector for recipe: {recipe["id"]}')
            recipes[index]['tasteScore'] = (1 - spatial.distance.cosine(recipe_vector, recipes_liked_vector))
            if index %100 == 0:
                print(f"index {index} out of {len(recipes)-1}")

            ####### COMPUTE NUTRITIONAL SCORE #######
            # print(f'Computing nutritional score for recipe {recipe["id"]}')
            profile = query_payload['profile']
            context = query_payload['context']

            goal_calories, goal_carbs, goal_protein, goal_fat = 0,0,0,0

            # calculate BMR based on information given
            if profile["weight"] and profile["heightFeet"] and profile["heightInches"] and profile["age"]:
                # BMR = 10 * weight in kg + 6.25 * height in cm - 5 * age + (5 if male, -161 if female)
                goal_calories = 10 * 0.453592 * profile["weight"] + \
                                6.25 * (30.48 * profile["heightFeet"] + 0.393701 * profile["heightInches"]) - \
                                5 * profile["age"]
                if profile["gender"] == "male":
                    goal_calories += 5
                else:
                    goal_calories -= 161
            else:                                   # if no information given, assume average BMR
                if profile["gender"] == "male":     # Based on daily consumption of 2500 calories per day
                    goal_calories = 2080
                else:                               # Based on daily consumption of 2000 calories per day
                    goal_calories = 1666
            
            # Apply multiplier based on activity level.
            if profile["activityLevel"] == "Lightly Active":
                goal_calories *= 1.375
            elif profile["activityLevel"] == "Moderately Active":
                goal_calories *= 1.55
            elif profile["activityLevel"] == "Very Active":
                goal_calories *= 1.725
            else: # Default = Sedentary
                goal_calories *= 1.2

            # Add calories based on steps taken today:
            if profile["weight"] and profile["heightFeet"] and profile["heightInches"]:
                # daily steps * (calories burned during 1 mile) * (strides per foot) / (feet per mile)
                goal_calories += context["dailySteps"] * (.57 * profile["weight"]) * (.414 * (profile["heightFeet"]  + profile["heightInches"]/12)) / 5280
            else:
                goal_calories += context["dailySteps"] * .04

            # Apply personal goals
            if profile["weeklyTarget"] == "Lose 2.0 lb/week":
                goal_calories -= 1000
            elif profile["weeklyTarget"] == "Lose 1.5 lb/week":
                goal_calories -= 750
            elif profile["weeklyTarget"] == "Lose 1.0 lb/week":
                goal_calories -= 500
            elif profile["weeklyTarget"] == "Lose 0.5 lb/week":
                goal_calories -= 250
            elif profile["weeklyTarget"] == "Gain 0.5 lb/week":
                goal_calories += 250
            elif profile["weeklyTarget"] == "Gain 1.0 lb/week":
                goal_calories += 500
            elif profile["weeklyTarget"] == "Gain 1.5 lb/week":
                goal_calories += 750
            else: # Default = Maintain weight
                goal_calories = goal_calories

            # Calculate Macros using suggested percentages: carbs = 70%, protein = 20%, fat = 10%
            goal_carbs = goal_calories * .7
            goal_protein = goal_calories * .2
            goal_fat = goal_calories * .1

            # Calculate total nutrition from today's eaten meals
            total_calories, total_carbs, total_protein, total_fat = 0,0,0,0
            for meal in context["mealsEaten"]:
                total_calories += meal["calories"]
                if 'carbs' in meal:
                    total_carbs += meal["carbs"] * 4
                if 'protein' in meal:
                    total_protein += meal["protein"] * 4
                if 'fat' in meal:
                    total_fat += meal["fat"] * 9

            # Subtract goal and total_eaten to get today's remaining nutrition
            query_vector = [
                goal_calories - total_calories,
                goal_carbs - total_carbs,
                goal_protein - total_protein,
                goal_fat - total_fat
            ]

            # Calculate this meal's values by dividing by how many meals left
            if context["currHour"] < 11:    # Morning: 3 meals left
                query_vector = [element / 3 for element in query_vector]
            elif context["currHour"] < 17:  # Afternoon: 2 meals left
                query_vector = [element / 2 for element in query_vector]
            else:                           # Default Evening: final meal
                query_vector = query_vector
                
            calories = recipe["calories"]['amount']
            carbs = recipe["carbohydrates"]['amount'] * 4
            protein = recipe["protein"]['amount'] * 4
            fat = recipe["fat"]['amount'] * 9

            recipe_vector = [calories, carbs, protein, fat]
            recipes[recipe]['nutritionalScore'] = (1 - spatial.distance.cosine(recipe_vector, query_vector, [3, 1, 1, 1])) 

    def _assemble_rankings(self, user_id, recipes, query_payload):
        likes = self._getLikesByUserId(user_id)
        tag_freqs = self._generate_tag_frequency_dict(user_id, recipes, likes)

        threads = []
        i = 0
        j = 500
        while True:
            if j > len(recipes):
                j = len(recipes)
            print(f"Starting batch thread for recipes {i} through {j}")
            th = threading.Thread(target=self._compute_scores, args=(recipes[i:j], likes, tag_freqs, query_payload, ))
            threads.append(th)
            th.start()

            if j == len(recipes):
                break # break case when all batch jobs are created for the entire list
            i = j; j += 500

        ### wait for all threads to finish computing scores
        for thread in threads:
            print("waiting for thread...")
            thread.join()
            print("batch thread finished")
        print("Returning recipes", recipes[0])
        return recipes

    def _generate_tag_frequency_dict(self, user_id, recipes, likes):
        tagFreqs = {}
        for like in likes:
            recipe = recipesCollection.find_one({'id': like['recipe_id']})
            if recipe == None:
                print("User liked a Recipe that does not exist!", like['recipe_id'])
                continue

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

            for tag in recipeTags:
                if tag in tagFreqs:
                    # print(f'recipe ${recipe["id"]} contains tag {tag}')
                    tagFreqs[tag] += 1
                else:
                    tagFreqs[tag] = 1
        return tagFreqs

    def _contains(self, recipes, recipe_id):
        for rid in recipes:
            if recipe_id == rid:
                return True
        return False
