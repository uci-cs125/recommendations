from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder
from app.utils.response import craftResp
from . import recsCollection
from .ranking import rank

import json
import pymongo
import requests

api = Namespace('recommendations', description='recommendation related operations')

recommendation = api.model('recommendation', {
    'message': fields.String(required=True, description='The message of the recommendation'),
    'goal': fields.Integer(required=True, description='The targeted goal by the recommendation')
})

parser = api.parser()
parser.add_argument('hour', type=int, required=True)
@api.route('/')
class RecommendationResource(Resource):
    @api.doc('list_recommendations')
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        currHour = int(args['hour'])

        mealType = None
        if currHour >= 11 and currHour <= 16:
            mealType = "brunch"
        elif currHour < 11:
            mealType = "breakfast"
        elif currHour > 16:
            mealType = "dinner"

        # mongo > db.find( { dishTypes: { $all: ["dinner"] } } )
        try:
            print("Fetching recommendations for meal type:", mealType)
            rankingResult = rank({"context": {"likes": [602443, 324412, 123123], "caloriesBurned": 483, "calorieGoal": 3000}})

            result = recsCollection.aggregate([{'$addFields': {"id": '$_id.oid'}}, { '$match': { 'dishTypes': { '$all': [mealType]}}}, { '$limit' : 20 }, ]) # only return the first 20 elements
            data = [doc for doc in result]
            return craftResp(data, request, 200)
        except:
            return craftResp('Error fetching recommendation list', request, 400)

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
