from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder
from app.utils.response import craftResp
from . import recipes_collection
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

@api.route('/')
class RecipeResource(Resource):
    @api.doc('list_recipes')
    @api.expect(parser)
    def post(self):
        args = parser.parse_args()
        currHour = 19
        uid = "bl1u5cdYmLb3TrYSFL8ub01qBiW2"

        try:
            body = request.get_json(force=True)
        except:
            body = {}

        mockPayload = {
            "profile": {
                "uid": uid,
                "age": 21,
                "gender": "Male",               # Male or Female
                "heightFeet": 5,
                "heightInches": 7,
                "weight": 125,
                "activityLevel": "Sedentary",        # Sedentary, Lightly Active, Moderately Active, Very Active
                "weeklyTarget": "Maintain my weight" # Maintain my weight, Lose 2.0 lb/week, Lose 1.5 lb/week, Lose 1.0 lb/week, Lose 0.5 lb/week, Gain 2.0 lb/week, Gain 1.5 lb/week, Gain 1.0 lb/week, Gain 0.5 lb/week
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
                "dailySteps": 0,
                "currHour": currHour
            }
        }

        if 'profile' in body and 'context' in body:
            mockPayload = body ## override mock data with real data from Swift frontend JSON bodys
            print("using json body for payload!")
            print("payload:", body)

        results = queryEngine.query(mockPayload)
        return craftResp(results, request, 200)
        # except:
            # return craftResp('Error fetching recipe list', request, 400)

    # @api.doc('create_recommendation', body=recommendation)
    # def post(self):
    #     body = request.get_json()
    #     # try:
    #     # result = recsClient.insert_one(body)
    #     print("json body:", body)
    #     # print("recs client:", recsClient)
    #     # if result.acknowledged:
    #     #     return craftResp(body, request, 200)
    #     # except pymongo.errors.DuplicateKeyError:
    #     #     return craftResp("Cannot create record: duplicate key exists.", request, 400)
    #     # except:
        #     return craftResp("Unknown state:", request, 400)
