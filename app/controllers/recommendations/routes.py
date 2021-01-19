from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder
from app.utils.response import craftResp
from . import recsClient
import json
import pymongo
import requests

api = Namespace('recommendations', description='recommendation related operations')

recommendation = api.model('recommendation', {
    'message': fields.String(required=True, description='The message of the recommendation'),
    'goal': fields.Integer(required=True, description='The targeted goal by the recommendation')
})

YELP_TOKEN = 'imY5RtK9SzacR1alCl1-Z2n9LR-jE5bOy2rZ51rgeln39AI3rOIO5_mWwfEC9rOIsyuDN4R26xAkEuYcOTRyJDNbP3c7G8Gw_YC-P3jrBN7U3e-rdi2kypOF2WsGYHYx'
@api.route('/')
class RecommendationResource(Resource):
    @api.doc('list_recommendations', params={
            'latitude': 'the latitude', 
            'longitude': 'the longitude',
            'term': 'the search term',
            'categories': 'the search categories'
        })
    def get(self):
        try:
            latitude = request.args.get('latitude')
            longitude = request.args.get('longitude')
            term = request.args.get('term') # breakfast, lunch, or dinner, for example
            categories = request.args.get('categories') # https://www.yelp.com/developers/documentation/v3/all_category_list
            url = 'https://api.yelp.com/v3/businesses/search?latitude=' + latitude + '&longitude=' + longitude + '&term=' + term + '&open_now=true' + '&categories=' + categories
            headers = {'Authorization': 'Bearer ' + YELP_TOKEN}

            print("request url:", url)
            # sending get request and saving the response as response object 
            r = requests.get(url = url, headers = headers)
            return craftResp(r.json(), request, 200)
        except:
            return craftResp('Error fetching recommendations', request, 400)


    @api.doc('create_recommendation', body=recommendation)
    def post(self):
        body = request.get_json()
        try:
            result = recsClient.insert_one(body)
            if result.acknowledged:
                return craftResp(body, request, 200)
        except pymongo.errors.DuplicateKeyError:
            return craftResp("Cannot create record: duplicate key exists.", request, 400)
