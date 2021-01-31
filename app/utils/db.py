import pymongo
import os

mongoClient = None

# Get Heroku MONGO_URL Config Var, else: use default of mongo:27017
try:

    addr = os.getenv("MONGO_URL", "mongo:27017")
    mongoClient = pymongo.MongoClient(addr)
    print("Initialized data base connection with url: ", addr)
    print("DB:", mongoClient.server_info())
except pymongo.errors.ServerSelectionTimeoutError as err:
    print("Failed to establish database client", err)