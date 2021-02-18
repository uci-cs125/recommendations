
import requests
from . import recipesCollection
from . import likedCollection
from scipy import spatial

class QueryEngine():
    def _assemble_liked_recipe_vector(self, user_id, recipes):
        print("Finding likes by user_id:", user_id)
        result = likedCollection.find({'user_id': user_id})
        likes = [like for like in result]

        if len(likes) == 0:
            print("User does not have any likes:", user_id)
            return []
        total_sweetness = 0
        total_saltiness = 0
        total_sourness = 0
        total_bitterness = 0;
        total_savoriness = 0
        total_fattiness = 0
        total_spiciness = 0
        for like in likes:
            recipe = recipesCollection.find_one({'id': like['recipe_id']})
            tasteProfile = recipe["tasteProfile"]

            total_sweetness += tasteProfile["sweetness"]
            total_saltiness += tasteProfile["saltiness"]
            total_sourness += tasteProfile["sourness"]
            total_bitterness += tasteProfile["bitterness"]
            total_savoriness += tasteProfile["savoriness"]
            total_fattiness += tasteProfile["fattiness"]
            total_spiciness += tasteProfile["spiciness"]

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
        print("constructed user's ideal query vector:", query_vector)


        ### construct recipe vector for all recipes
        recipe_vectors = []
        recipe_scores = []
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
            recipes[index]['similarityScore'] = similarity
            recipe_scores.append(similarity)
            if recipe['id'] == 655055:
                print("FOUND RECIPE:")
        sorted_recipes = sorted(recipes, key = lambda i: i['similarityScore'],reverse=True)
        return sorted_recipes


    def query(self, payload):   

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
            { 
                '$match': { 
                    'dishTypes': { 
                        '$all': [mealType]
                    }
                }
            }, 
            {
                '$project': {
                    'title': 1, 
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
                    }
                }
            ])
        recipes = [doc for doc in result]

        recommendations = self._assemble_liked_recipe_vector(context["uid"], recipes)
        print("First recommendation:", recommendations[0]['id'], "with score of:", recommendations[0]['similarityScore'])
        return recommendations[:20]