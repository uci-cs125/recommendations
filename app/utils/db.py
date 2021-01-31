import pymongo
import os

mongoClient = {}

# Get Heroku MONGO_URL Config Var, else: use default of mongo:27017
addr = os.getenv("MONGO_URL", "mongo:27017")
mongoClient = pymongo.MongoClient(addr)
