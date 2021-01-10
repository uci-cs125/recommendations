import pymongo

mongoClient = pymongo.MongoClient('mongo:27017')
usersClient = mongoClient.engine["users"]
usersClient.create_index(
    [("username", pymongo.DESCENDING)],
    unique=True
)