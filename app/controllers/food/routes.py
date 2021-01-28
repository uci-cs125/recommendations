from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder, DateTimeEncoder
from app.utils.response import craftResp
import json
import pymongo
from . import usersClient, authClient
import traceback
from flask_bcrypt import Bcrypt
import jwt, datetime

bcrypt = Bcrypt()

api = Namespace('users', description='users related operations')
authRequest = api.model('auth', {
    'username': fields.String(required=True, description='The username of the authnetication request'),
    'password': fields.String(required=True, description='the password of the authentication request')
})

user = api.model('user', {
    'username': fields.String(required=True, description='username of the user'),
    'password': fields.String(required=True, description='password of the user'),
    'age': fields.Integer(required=True, description='age of the user'),
    'height': fields.Integer(required=True, description='height of the user in inches'),
    'weight': fields.Float(required=True, description='weight of the user in lbs'),
    'gender': fields.String(required=True, description='gender of the user'),
    'favoritePlaces': fields.List(fields.String, required=True, description='The favorite places of the user'),
    'name': fields.Nested(api.model('name', {
        'firstName': fields.String(),
        'lastName': fields.String()
    })),
    'dob': fields.Nested(api.model('dob', {
        'month': fields.Integer(),
        'day': fields.Integer(),
        'year': fields.Integer()
    })),
    'workAddress': fields.Nested(api.model('workAddress', {
        'address': fields.String(),
        'city': fields.String(),
        'state': fields.String(),
        'zip': fields.Integer(),
        'country': fields.String(),
    })),
    'homeAddress': fields.Nested(api.model('homeAddress', {
        'address': fields.String(),
        'city': fields.String(),
        'state': fields.String(),
        'zip': fields.Integer(),
        'country': fields.String(),
    })),
    'goal': fields.Nested(api.model('goal', {
        'description': fields.String(description="The description of the goal, ie gain weight, increase energy, etc"),
        'dailySteps': fields.Integer(description="The daily step goal for the user")
    })),
    'foodPreferences': fields.Nested(api.model('foodPreferences', {
        'dishes': fields.List(fields.String),
        'likes': fields.String(),
        'dislikes': fields.String(),
        'allergies': fields.Integer()
    }))
})


@api.route('/')
class UserResource(Resource):
    @api.doc('list_users')
    def get(self):
        try:
            result = usersClient.aggregate([{'$addFields': {"id": '$_id.oid'}}])
            data = [doc for doc in result]
            
            return craftResp(data, request, 200)
        except:
            return craftResp('Error fetching user list', request, 400)

    @api.doc('create_user', body=user)
    def post(self):
        body = request.get_json()
        try:
            # Hash the password
            print("raw pass:", body['password'])
            hashedPass = bcrypt.generate_password_hash(body['password'])
            print('Hashed pass', hashedPass)
            body['password'] = hashedPass.decode("utf-8") 

            result = usersClient.insert_one(body)
            if result.acknowledged:
                return craftResp(body, request, 200)
        except pymongo.errors.DuplicateKeyError:
            return craftResp("Cannot create record: duplicate key exists. Ensure username is unique.", request, 400)
        except:
            traceback.format_exc()
            return craftResp("Error encountered", request, 500)


    # @api.route('/<id>')
    # @api.param('id', 'The user identifier')
    # @api.response(404, 'user not found')
    # class user(Resource):s
    #     @api.doc('get_user')
    #     def get(self, id):
    #         '''Fetch a user given its identifier'''
    #         for user in users:
    #             if user['id'] == id:
    #                 return user
    #         api.abort(404)
