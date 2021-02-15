import pymongo
import os

mongoClient = None
# Get Heroku MONGO_URL Config Var, else: use default of mongo:27017
try:
    addr = os.getenv("MONGO_URL", "mongodb+srv://developer:developer@recommendations.g25bt.mongodb.net/<dbname>?retryWrites=true&w=majority")
    mongoClient = pymongo.MongoClient(addr)
    print("Initialized data base connection with url: ", addr)
    print("--------------------------------------------------------")
    print("DB Initialized:")
    print("--------------------------------------------------------")
    print(mongoClient.server_info())

except pymongo.errors.ServerSelectionTimeoutError as err:
    print("Failed to establish database client", err)