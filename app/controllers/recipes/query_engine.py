
import requests
from . import recipes_collection
from . import liked_collection
from scipy import spatial
from threading import Thread, Lock
import time
import pymongo
from app.utils.calculator import calculate_calories

class QueryEngine():
    def __init__(self):
        recipes = recipes_collection.find({}, batch_size=20000, cursor_type=pymongo.cursor.CursorType.EXHAUST)
        print('got recipes')
        self.recipes = [r for r in recipes]
        print('assembled all recipes list:', len(self.recipes))

    def query(self, payload):
        print(f'received query payload: {payload}')

        # rank and sort self.recipes
        return self._rank_and_sort(payload)

    def _rank_and_sort(self, query_payload):
        user_id = query_payload['profile']['uid']

        ## liked recipes
        liked_recipe_ids = self._getLikedRecipeIDsByUID(user_id) # get all recipe ids that the user liked
        print('got user\'s liked recipe ids:', liked_recipe_ids)
        liked_recipes = recipes_collection.find({'id': {'$in': liked_recipe_ids}}) # get all recipes that the user liked
        liked_recipes = [recipe for recipe in liked_recipes]

        recipes_liked_taste_vector = self._get_recipes_liked_taste_vector(liked_recipes) # get ideal taste vector

        # tag frequency dictionary
        tag_freqs = self._generate_tag_frequency_dict(user_id, liked_recipes)
        
        print(f'\n\ntags_freqs: {tag_freqs}\n\nrecipes_liked vector: {recipes_liked_taste_vector}\n')
        ranked_recipes = self._compute_scores(recipes_liked_taste_vector, liked_recipe_ids, tag_freqs, query_payload)

        hasLikes = False
        if len(liked_recipes) > 0:
            hasLikes = True
        return self._sort_recipes_by_rank(ranked_recipes, hasLikes) # sort recipes by rank

    def _sort_recipes_by_rank(self, recipes, hasLikes):
        recommendations_by_nutrition = sorted(recipes, key = lambda i: i['nutritionalScore'], reverse=True)

        if hasLikes:
            print("user has likes, returning mixture of recommendations by tag, taste, nutrition, and weighted sum.")
            recommendations_by_tag = sorted(recipes, key = lambda i: i['tagScore'], reverse=True)
            recommendations_by_taste = sorted(recipes, key = lambda i: i['tasteScore'], reverse=True)
            recommendations_by_mix = sorted(recipes, 
                                        key = lambda i: (i['tagScore'] * .15 + i['tasteScore'] * .10 + i['nutritionalScore'] * .75), 
                                        reverse=True)
            interweaved = [val for pair in zip(
                            recommendations_by_tag, 
                            recommendations_by_taste, 
                            recommendations_by_nutrition, 
                            recommendations_by_mix) for val in pair]

            return interweaved[:50]
        
        print("[ debug ]: user has no likes, only recommending based on nutritional value.")
        return recommendations_by_nutrition[:50] # if the user hasn't liked anything, we can only rank by nutritional info.

    def _compute_scores(self, recipes_liked_taste_vector, liked_recipe_ids, tag_freqs, query_payload):
        results = []
        for index, recipe in enumerate(self.recipes):
            recipe['tasteScore'] = 0
            recipe['nutritionalScore'] = 0
            recipe['tagScore'] = 0
            if recipe['id'] in liked_recipe_ids:
                print(f'excluding recipe {recipe["id"]} from recommendations because user liked it recently.')
                continue

            recipe['tasteScore'] = self._compute_taste_score(recipes_liked_taste_vector, recipe)
            recipe['nutritionalScore'] = self._compute_nutritional_score(query_payload, recipe)
            recipe['tagScore'] = self._compute_tag_score(tag_freqs, recipe)
            results.append(recipe)
        return results

    def _getLikedRecipeIDsByUID(self, user_id):
        result = liked_collection.find({'user_id': user_id})
        liked_recipe_ids = [like['recipe_id'] for like in result]
        if len(liked_recipe_ids) == 0:
            print('User does not have any likes:', user_id)
            return []

        return liked_recipe_ids

    def _get_recipes_liked_taste_vector(self, liked_recipes):
        print('_get_recipes_liked_taste_vector::liked_recipes', liked_recipes)
        total_sweetness, total_saltiness, total_sourness, total_bitterness, \
        total_savoriness, total_fattiness, total_spiciness = 0,0,0,0,0,0,0

        total_likes = 0
        for recipe in liked_recipes:
            tasteProfile = recipe['tasteProfile']
            total_sweetness += tasteProfile['sweetness']
            total_saltiness += tasteProfile['saltiness']
            total_sourness += tasteProfile['sourness']
            total_bitterness += tasteProfile['bitterness']
            total_savoriness += tasteProfile['savoriness']
            total_fattiness += tasteProfile['fattiness']
            total_spiciness += tasteProfile['spiciness']
            total_likes += 1

        if total_likes == 0:
            return []

        # return average taste vector
        return [
            total_sweetness/total_likes, 
            total_saltiness/total_likes, 
            total_sourness/total_likes, 
            total_bitterness/total_likes, 
            total_savoriness/total_likes, 
            total_fattiness/total_likes, 
            total_spiciness/total_likes
        ]

    def _compute_tag_score(self, tag_freqs, recipe):
        if len(tag_freqs) == 0:
            return 0

        total_freqs = 0
        recipeTagScore = 0
        for tag in tag_freqs:
            total_freqs += tag_freqs[tag]
        # print('tag freqs:', tag_freqs)
        # print('total_freqs:', total_freqs)

        for tag in tag_freqs:
            if tag in recipe['tags']:
                recipeTagScore += (tag_freqs[tag]/total_freqs)
        # print('computed tag score:', recipeTagScore)
        return recipeTagScore

    def _compute_taste_score(self, recipes_liked_taste_vector, recipe):
        if len(recipes_liked_taste_vector) == 0:
            return 0

        recipe_profile = recipe['tasteProfile']
        recipe_vector = [recipe_profile['sweetness'], recipe_profile['saltiness'], recipe_profile['sourness'], 
                            recipe_profile['bitterness'], recipe_profile['savoriness'], recipe_profile['fattiness'], 
                            recipe_profile['spiciness']]
        return (1 - spatial.distance.cosine(recipe_vector, recipes_liked_taste_vector))

    def _compute_nutritional_score(self, query_payload, recipe):
        '''
            Appends nutritionalScore  for the given recipe and query_payload,
            where 'nutritionalScore' is the cosine similarity between
            nutrients of the recipe and the nutrients needed for the user's goal
        '''
        profile = query_payload['profile']
        context = query_payload['context']
        goal_calories = calculate_calories(profile)

        # Add calories based on steps taken today:
        if 'weight' in profile and 'heightFeet' in profile and 'heightInches' in profile:
            # daily steps * (calories burned during 1 mile) * (strides per foot) / (feet per mile)
            goal_calories += context['dailySteps'] * (.57 * profile['weight']) * (.414 * (profile['heightFeet']  + profile['heightInches']/12)) / 5280
        else:
            if 'dailySteps' in context:
                goal_calories += context['dailySteps'] * .04

        # Calculate Macros using suggested percentages: carbs = 70%, protein = 20%, fat = 10%
        goal_carbs = goal_calories * .7
        goal_protein = goal_calories * .2
        goal_fat = goal_calories * .1

        # Calculate total nutrition from today's eaten meals
        total_calories = 0
        total_carbs = 0
        total_protein = 0
        total_fat = 0
        for meal in context['mealsEaten']:
            total_calories += meal['calories']
            if 'carbs' in meal:
                total_carbs += meal['carbs'] * 4
            if 'protein' in meal:
                total_protein += meal['protein'] * 4
            if 'fat' in meal:
                total_fat += meal['fat'] * 9

        # Subtract goal and total_eaten to get today's remaining nutrition
        query_vector = [
            goal_calories - total_calories,
            goal_carbs - total_carbs,
            goal_protein - total_protein,
            goal_fat - total_fat
        ]

        # Calculate this meal's values by dividing by how many meals left
        if context['currHour'] < 11:    # Morning: 3 meals left
            query_vector = [element / 3 for element in query_vector]
        elif context['currHour'] < 17:  # Afternoon: 2 meals left
            query_vector = [element / 2 for element in query_vector]
        else:                           # Default Evening: final meal
            query_vector = query_vector
            
        ### construct recipe vector for the given recipe
        calories = recipe['calories']['amount']
        carbs = recipe['netCarbohydrates']['amount'] * 4
        protein = recipe['protein']['amount'] * 4
        fat = recipe['fat']['amount'] * 9

        vec = [calories, carbs, protein, fat]
        return (1 - spatial.distance.cosine(vec, query_vector, [3, 1, 1, 1])) # weighted with calories taking higher precedence

    def _generate_tag_frequency_dict(self, user_id, liked_recipes):
        tagFreqs = {}
        for recipe in liked_recipes:
            for tag in recipe['tags']:
                if tag in tagFreqs:
                    # print(f'recipe ${recipe["id"]} contains tag {tag}')
                    tagFreqs[tag] += 1
                else:
                    tagFreqs[tag] = 1
        return tagFreqs
