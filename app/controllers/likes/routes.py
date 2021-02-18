from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder
from app.utils.response import craftResp
from . import likesCollection
import json
import pymongo
import requests

api = Namespace('likes', description='user recipe likes')

like = api.model('like', {
    'user_id': fields.Integer(required=True, description='The user id that liked the recipe'),
    'recipe_id': fields.Integer(required=True, description='The liked recipe id')
})

parser = api.parser()
parser.add_argument('user_id', type=int, required=True)
@api.route('/')
class LikeResource(Resource):
    @api.doc('list_likes')
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        userID = int(args['user_id'])

        try:
            result = likesCollection.find({'user_id': userID}) # only return the first 20 elements
            data = [doc for doc in result]
            return craftResp(data, request, 200)
        except:
            return craftResp('Error fetching like list', request, 400)

    @api.doc('create_like', body=like)
    def post(self):
        body = request.get_json()
        # try:
        result = likesCollection.insert_one(body)
        if result.acknowledged:
            return craftResp(body, request, 200)
        print("Result:", result)
        # except pymongo.errors.DuplicateKeyError:
        #     return craftResp("Cannot create record: duplicate key exists.", request, 400)
        # except:
        #     return craftResp("Unknown state:", result, 400)
