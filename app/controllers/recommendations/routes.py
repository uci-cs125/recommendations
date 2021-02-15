from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder
from app.utils.response import craftResp
from . import recsCollection

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
args = parser.parse_args()

@api.route('/')
class RecommendationResource(Resource):
    @api.doc('list_recommendations')
    @api.expect(parser)
    def get(self):
        try:
            print("Fetching recommendations for current hour:", args['hour'])
            result = recsCollection.aggregate([{'$addFields': {"id": '$_id.oid'}}, { '$limit' : 5 }]) # only return the first 20 elements
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
