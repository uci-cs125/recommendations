
import requests
from . import recipesCollection
class QueryEngine():
    def query(self, payload):
        context = payload["context"]
        print("QUERY")
        mealType = None
        if context["currHour"] >= 11 and context["currHour"] <= 16:
            mealType = "brunch"
        elif context.currHour < 11:
            mealType = "breakfast"
        elif context.currHour > 16:
            mealType = "dinner"
        result = recipesCollection.aggregate([{ '$match': { 'dishTypes': { '$all': [mealType]}}}, {'$project': {'title': 1, 'id': 1, 'nutrition': 1, 'dishTypes': 1, 'diets': 1, 'cuisines': 1, 'vegetarian': 1, 'image': 1, 'vegan': 1, 'glutenFree': 1, 'dairyFree': 1, 'sustainable': 1, 'cheap': 1, 'veryHealthy': 1, 'aggregateLikes': 1}}, { '$limit' : 20 }]) # only return the first 20 elements
        data = [doc for doc in result]
        return data