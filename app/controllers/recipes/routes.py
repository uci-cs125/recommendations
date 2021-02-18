from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder
from app.utils.response import craftResp
from . import recipesCollection
import json
from .query_engine import QueryEngine
import pymongo
import requests

queryEngine = QueryEngine()
api = Namespace('recipes', description='recommendation related operations')

recommendation = api.model('recipes', {
    'message': fields.String(required=True, description='The message of the recommendation'),
    'goal': fields.Integer(required=True, description='The targeted goal by the recommendation')
})

parser = api.parser()
parser.add_argument('hour', type=int, required=True)
parser.add_argument('uid', required=True)

@api.route('/')
class RecipeResource(Resource):
    @api.doc('list_recipes')
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        currHour = int(args['hour'])
        uid = args['uid']

        # mongo > db.find( { dishTypes: { $all: ["dinner"] } } )
        # try:

        payload = {
            "profile": {
                "uid": uid,
                "age": 21,
                "sex": 1,               # 0 = male, 1 = female or other
                "heightFeet": 5,
                "heightInches": 7,
                "weight": 125,
                "averageActivity": 1,   #0 = sedentary, 1 = light exercise, 2 = moderate exercise daily, 3 = hard exercise daily, 4 = hard exercise 2+ per day
                "goal": 2               # 0 = lose, 1 = maintain, 2 = gain
            },
            "context": {
                "mealsEaten": [
                    {
                        "calories" : 400,
                        "fat" : 10,
                        "carbs" : 100,
                        "protein" : 10,
                    },
                    {
                        "calories" : 160,
                        "fat" : 0,
                        "carbs" : 40,
                        "protein" : 0,
                    }
                ],
                "caloriesBurned": 3000,
                "currHour": currHour
            }
        }
        
        results = queryEngine.query(payload)
        return craftResp(results, request, 200)
        # except:
            # return craftResp('Error fetching recipe list', request, 400)

    @api.doc('create_recommendation', body=recommendation)
    def post(self):
        body = request.get_json()
        # try:
        # result = recsClient.insert_one(body)
        print("json body:", body)
        # print("recs client:", recsClient)
        # if result.acknowledged:
        #     return craftResp(body, request, 200)
        # except pymongo.errors.DuplicateKeyError:
        #     return craftResp("Cannot create record: duplicate key exists.", request, 400)
        # except:
        #     return craftResp("Unknown state:", request, 400)
