from flask_restplus import Api
import os

from .controllers.recipes.routes import api as recipesAPI
from .controllers.likes.routes import api as likesAPI
from .controllers.calories.routes import api as caloriesAPI

api = Api(
    title='Recommendation Engine API',
    version='1.0',
    description='<b>Environment: ' + os.getenv("ENVIRONMENT", "dev") + '</b>\nA simple API for recommendations',
)

# api.add_namespace(usersAPI)
api.add_namespace(recipesAPI)
api.add_namespace(likesAPI)
api.add_namespace(caloriesAPI)