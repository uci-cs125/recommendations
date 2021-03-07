from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder
from app.utils.response import craftResp
from app.utils.calculator import calculate_calories
import json
import pymongo
import requests

api = Namespace('calories', description='user daily calories')

recommendation = api.model('calories', {
    'message': fields.String(required=True, description='The profile of the user')
})

parser = api.parser()

@api.route('/')
class CalorieResource(Resource):
    @api.doc('list_calories')
    @api.expect(parser)
    def post(self):
        args = parser.parse_args()
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
            }
        }

        if 'profile' in body:
            mockPayload = body ## override mock data with real data from Swift frontend JSON bodys
            print("using json body for payload!")

        results = calculate_calories(mockPayload['profile'])
        print("Calculated Base Calories:", results)
        return craftResp([results], request, 200)
