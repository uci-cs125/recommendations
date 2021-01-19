from app.utils.db import mongoClient

## Set up the recommendations database connection
recsClient = mongoClient.recommendations["recommendations"]