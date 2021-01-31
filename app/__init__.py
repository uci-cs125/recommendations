from flask_restplus import Api

from .controllers.recommendations.routes import api as recsAPI

api = Api(
    title='Recommendation Engine API',
    version='1.0',
    description='A simple API for recommendations and users',
)

api.add_namespace(usersAPI)
api.add_namespace(recsAPI)

