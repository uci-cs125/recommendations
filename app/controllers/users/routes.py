from flask_restplus import Namespace, Resource, fields, reqparse
from flask import jsonify, Response, request
from bson.json_util import dumps, loads
from bson import json_util
from app.utils.encoder import JSONEncoder
import json
import pymongo
from app.controllers.users import usersClient

api = Namespace('users', description='users related operations')

user = api.model('user', {
    'username': fields.String(required=True, description='The username of the user'),
    'age': fields.Integer(required=True, description='The age of the user'),
    'height': fields.Integer(required=True, description='The height of the user in inches'),
    'weight': fields.Float(required=True, description='The weight of the user in lbs'),
})


@api.route('/')
class UserResource(Resource):
    @api.doc('list_users')
    def get(self):
        try:
            print("USERS CLIENT")
            print(usersClient)
            result = usersClient.aggregate([{'$addFields': {"id": '$_id.oid'}}])
            data = [doc for doc in result]

            return Response(json.dumps({'data': data}, cls=JSONEncoder), mimetype='application/json')
        except:
            return Response(json.dumps({'data': 'Error fetching user list'}), 400)

    @api.doc('create_user', body=user)
    def post(self):
        body = request.get_json()
        try:
            result = usersClient.insert_one(body)
            if result.acknowledged:
                print("inserted user with id:", result.inserted_id)
                return Response(json.dumps({'data': body}, cls=JSONEncoder), mimetype='application/json')
        except pymongo.errors.DuplicateKeyError:
            return Response(json.dumps({'data': 'Cannot create record: duplicate key exists. Ensure username is unique.'}), 400)





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
