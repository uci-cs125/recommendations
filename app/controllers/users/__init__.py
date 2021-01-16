import pymongo
## Set up the users database connection and ensure the username field is indexed uniquely
mongoClient = pymongo.MongoClient('mongo:27017')
usersClient = mongoClient.users["users"]
usersClient.create_index(
    [("username", pymongo.DESCENDING)],
    unique=True
)