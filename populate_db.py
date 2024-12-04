from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['nutritionist_app']
collection = db['patients']

# Correct data structure
data = [
    {
        "name": f"Patient {i + 1}",
        "BMI": 18.5 + (i % 15),
        "blood_metrics": {
            "glucose_levels": {  # Adding the missing glucose_levels key
                "FBPS": 80 + (i % 50),
                "PPBS": 100 + (i % 100),
            },
            "HbA1c": 5.0 + (i % 10) / 10,
            "cholesterol": {
                "LDL": 100 + (i % 100),
                "HDL": 40 + (i % 30),
                "triglycerides": 150 + (i % 200),
            },
        },
        "physical_activity": "high" if i % 3 == 0 else "low" if i % 2 == 0 else "moderate",
        "diet_type": "balanced" if i % 4 == 0 else "low-carb" if i % 3 == 0 else "high-protein",
    }
    for i in range(1000)
]

# Insert corrected data into MongoDB
result = collection.insert_many(data)
print(f"{len(result.inserted_ids)} records inserted successfully into MongoDB!")
