import pymongo
from app.utils.db import mongoClient

## Set up the users database connection and ensure the username field is indexed uniquely
usersClient = mongoClient.users["users"]
usersClient.create_index(
    [("username", pymongo.DESCENDING)],
    unique=True
)

authClient = mongoClient.users["authStore"]