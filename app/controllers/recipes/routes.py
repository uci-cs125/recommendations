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
@api.route('/')
class RecipeResource(Resource):
    @api.doc('list_recipes')
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        currHour = int(args['hour'])

        # mongo > db.find( { dishTypes: { $all: ["dinner"] } } )
        # try:

        payload = {
            "context": {
                "likes": [766453, 640941, 123123], 
                "caloriesBurned": 483, 
                "calorieGoal": 3000,
                "currHour": 15
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
