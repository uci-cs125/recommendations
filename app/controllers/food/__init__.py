import pymongo
from app.utils.db import mongoClient

## Set up the database connection and ensure the appropriate field is indexed
# usersClient = mongoClient.users["users"]
# usersClient.create_index(
#     [("username", pymongo.DESCENDING)],
#     unique=True
# )
