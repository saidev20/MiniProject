from pymongo import MongoClient
import pprint

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['nutritionist_app']
patients_collection = db['patients']

# Fetch and display all records
patients = list(patients_collection.find({}, {"_id": 0}))
pprint.pprint(patients)
