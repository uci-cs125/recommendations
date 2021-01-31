from flask_restplus import Api
import os

from .controllers.recommendations.routes import api as recsAPI

api = Api(
    title='Recommendation Engine API',
    version='1.0',
    description='<b>Environment: ' + os.getenv("ENVIRONMENT", "dev") + '</b>\nA simple API for recommendations',
)

# api.add_namespace(usersAPI)
api.add_namespace(recsAPI)

