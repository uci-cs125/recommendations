from flask_restplus import Namespace, Resource, fields

api = Namespace('recommendations', description='recommendation related operations')

recommendation = api.model('recommendation', {
    'id': fields.String(required=True, description='The UID of the recommendation'),
    'msg': fields.String(required=True, description='The msg of the recommendations'),
})

recommendations = [
    {'id': '1', 'msg': 'Go for a run today'},
    {'id': '2', 'msg': 'Go to bed earlier today'},
]

@api.route('/')
class recommendationsList(Resource):
    @api.doc('list_recommendations')
    @api.marshal_list_with(recommendation)
    def get(self):
        '''Fetch all recommendations'''
        return recommendations


@api.route('/<id>')
@api.param('id', 'The recommendation identifier')
@api.response(404, 'recommendation not found')
class recommendation(Resource):
    @api.doc('get_recommendations')
    @api.marshal_with(recommendation)
    def get(self, id):
        '''Fetch a recommendation given its identifier'''
        for rec in recommendations:
            if rec['id'] == id:
                return rec
        api.abort(404)
