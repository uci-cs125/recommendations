
import requests
from . import recipesCollection
from . import likedCollection
from scipy import spatial

class QueryEngine():
    def _assemble_taste_rankings(self, user_id, recipes):
        '''
            Appends recipes[i]['tasteScore'] to recipes list
            where 'tasteScore' is the cosine similarity between
            the flavor profile of the meal and the user's liked recipes
        '''
        # init with all zeros
        for index, recipe in enumerate(recipes):
            recipes[index]['tasteScore'] = 0

        print("Finding likes by user_id:", user_id)
        result = likedCollection.find({'user_id': user_id})
        likes = [like for like in result]

        if len(likes) == 0:
            print("User does not have any likes:", user_id)
            return recipes

        total_sweetness = 0
        total_saltiness = 0
        total_sourness = 0
        total_bitterness = 0
        total_savoriness = 0
        total_fattiness = 0
        total_spiciness = 0
        for like in likes:
            recipe = recipesCollection.find_one({'id': like['recipe_id']})
            if recipe == None:
                print("User liked a Recipe that does not exist!", like['recipe_id'])
                continue
            
            tasteProfile = recipe["tasteProfile"]

            total_sweetness += tasteProfile["sweetness"]
            total_saltiness += tasteProfile["saltiness"]
            total_sourness += tasteProfile["sourness"]
            total_bitterness += tasteProfile["bitterness"]
            total_savoriness += tasteProfile["savoriness"]
            total_fattiness += tasteProfile["fattiness"]
            total_spiciness += tasteProfile["spiciness"]
            print("user liked recipe:", tasteProfile)
        print("Total sweetness:", total_sweetness)
        avg_sweetness = total_sweetness/len(likes)
        avg_saltiness = total_saltiness/len(likes)
        avg_sourness = total_sourness/len(likes)
        avg_bitterness = total_bitterness/len(likes)
        avg_savoriness = total_savoriness/len(likes)
        avg_fattiness = total_fattiness/len(likes)
        avg_spiciness = total_spiciness/len(likes)
        query_vector = [
            avg_sweetness, 
            avg_saltiness, 
            avg_sourness, 
            avg_bitterness, 
            avg_savoriness, 
            avg_fattiness, 
            avg_spiciness
        ]
        print("constructed user's taste query vector:", query_vector)

        ### construct recipe vector for all recipes
        recipe_vectors = []
        for index, recipe in enumerate(recipes):
            if 'tasteProfile' not in recipe.keys():
                print("Recipe is missing tasteProfile field!:", recipe)
                continue
            tasteProfile = recipe['tasteProfile']

            sweetness = tasteProfile['sweetness']
            saltiness = tasteProfile['saltiness']
            sourness = tasteProfile['sourness']
            bitterness = tasteProfile['bitterness']
            savoriness = tasteProfile['savoriness']
            fattiness = tasteProfile['fattiness']
            spiciness = tasteProfile['spiciness']

            vec = [sweetness, saltiness, sourness, bitterness, savoriness, fattiness, spiciness]
            similarity = 1 - spatial.distance.cosine(vec, query_vector)
            recipes[index]['tasteScore'] = similarity
        return recipes

    def _assemble_nutritional_rankings(self, profile, context, recipes):
        '''
            Appends recipes[i]['nutritionalScore'] to recipes list
            where 'nutritionalScore' is the cosine similarity between
            nutrients of the meal and the nutrients needed for the user's goal
        '''
        goal_calories = 0
        goal_carbs = 0
        goal_protein = 0
        goal_fat = 0

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
        elif profile["weeklyTarget"]== "Lose 1.0 lb/week":
            goal_calories -= 500
        elif profile["weeklyTarget"]== "Lose 0.5 lb/week":
            goal_calories -= 250
        elif profile["weeklyTarget"]== "Gain 0.5 lb/week":
            goal_calories += 250
        elif profile["weeklyTarget"]== "Gain 1.0 lb/week":
            goal_calories += 500
        elif profile["weeklyTarget"]== "Gain 1.5 lb/week":
            goal_calories += 750
        else: # Default = Maintain weight
            goal_calories = goal_calories

        # Calculate Macros using suggested percentages: carbs = 70%, protein = 20%, fat = 10%
        goal_carbs = goal_calories * .7
        goal_protein = goal_calories * .2
        goal_fat = goal_calories * .1

        # Calculate total nutrition from today's eaten meals
        total_calories = 0
        total_carbs = 0
        total_protein = 0
        total_fat = 0
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
            
        print("constructed user's nutritional query vector:", query_vector)

        ### construct recipe vector for all recipes
        recipe_vectors = []
        for index, recipe in enumerate(recipes):

            calories = recipe["nutrition"]['nutrients'][0]['amount']
            carbs = recipe["nutrition"]['nutrients'][1]['amount'] * 4
            protein = recipe["nutrition"]['nutrients'][4]['amount'] * 4
            fat = recipe["nutrition"]['nutrients'][8]['amount'] * 9

            vec = [calories, carbs, protein, fat]
            similarity = 1 - spatial.distance.cosine(vec, query_vector, [3, 1, 1, 1]) # weighted with calories taking higher precedence
            recipes[index]['nutritionalScore'] = similarity
        return recipes

    def query(self, payload):
        profile = payload["profile"]
        context = payload["context"]
        # print("QUERY context:", context)
        mealType = None
        if context["currHour"] >= 11 and context["currHour"] <= 16:
            mealType = "brunch"
        elif context["currHour"] < 11:
            mealType = "breakfast"
        elif context["currHour"] > 16:
            mealType = "dinner"
        # print("meal type:", mealType)
        result = recipesCollection.aggregate([
            # { 
            #     '$match': { 
            #         'dishTypes': { 
            #             '$all': [mealType]
            #         }
            #     }
            # }, 
            {
                '$project': {
                    'title': 1, 
                    'sourceUrl': 1,
                    'id': 1, 
                     'dishTypes': 1, 
                     'diets': 1, 
                     'cuisines': 1,
                      'vegetarian': 1, 
                      'image': 1,
                       'vegan': 1, 
                       'glutenFree': 1, 
                       'dairyFree': 1, 
                       'sustainable': 1, 
                       'cheap': 1, 
                       'veryHealthy': 1, 
                       'aggregateLikes': 1,
                       'tasteProfile': 1,
                       'nutrition': 1,
                       'carbohydrates': 1,
                       'netCarbohydrates': 1,
                       'protein': 1,
                       'fiber': 1,
                       'sugar': 1,
                       'calories': 1,
                       'fat': 1,
                       'saturatedFat': 1,
                       'cholesterol': 1,
                       'sodium': 1
                    }
                }
            ])
        recipes = [doc for doc in result]

        recipes = self._assemble_nutritional_rankings(profile, context, recipes)
        recipes = self._assemble_taste_rankings(profile["uid"], recipes)
        recommendations = sorted(recipes, \
                                key = lambda i: i['nutritionalScore']*.5 + \
                                                i['tasteScore']*.5, \
                                reverse=True)
        print("First recommendation: ", recommendations[0]['id'], " with score of: ", recommendations[0]['nutritionalScore']*.5+recommendations[0]['tasteScore']*.5)
        return recommendations[:50]