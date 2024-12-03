import random
import numpy as np
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['nutritionist_app']
patients_collection = db['patients']

# Clear existing data
patients_collection.delete_many({})

# Generate 100 mock patient records
data = []
for i in range(1000):
    # Generate health metrics
    BMI = round(np.random.normal(25.0, 5.0), 1)  # Mean BMI ~25, std dev ~5
    physical_activity = random.choice(["low", "moderate", "high"])
    HbA1c = round(np.random.uniform(4.5, 14.0), 1)  # Random HbA1c between 4.5 and 14
    LDL = int(np.random.normal(120, 30))  # Mean LDL ~120, std dev ~30
    HDL = random.randint(30, 70)  # HDL typically ranges from 30-70
    triglycerides = random.randint(50, 300)  # Typical range ~50-300
    FBPS = random.randint(70, 150)  # Fasting blood sugar
    PPBS = random.randint(100, 250)  # Post-prandial blood sugar

    # Determine diet type based on health metrics
    if HbA1c >= 8.0 or FBPS > 120 or PPBS > 200:
        diet_type = "low-carb"  # For uncontrolled diabetes or high glucose
    elif HbA1c >= 6.5 and HbA1c < 8.0 or FBPS >= 110 and FBPS <= 120 or PPBS >= 180 and PPBS <= 200:
        diet_type = "moderate-carb"  # For controlled diabetes or prediabetes
    elif HbA1c >= 5.7 and HbA1c < 6.5 or HDL < 40 or triglycerides > 200:
        diet_type = "high-protein"  # For prediabetes or lipid profile improvement
    elif LDL > 160 or (FBPS >= 100 and FBPS < 110) or (PPBS >= 140 and PPBS < 180):
        diet_type = "low-fat"  # For cholesterol issues or mild glucose problems
    else:
        diet_type = "balanced"  # For healthy individuals

    # Create patient record
    patient = {
        "name": f"Patient {i+1}",
        "blood_metrics": {
            "glucose_levels": {
                "FBPS": FBPS,
                "PPBS": PPBS
            },
            "HbA1c": HbA1c,
            "cholesterol": {
                "LDL": LDL,
                "HDL": HDL,
                "triglycerides": triglycerides
            }
        },
        "BMI": BMI,
        "physical_activity": physical_activity,
        "diet_type": diet_type
    }
    data.append(patient)

# Insert the generated data into MongoDB
patients_collection.insert_many(data)

print(f"Mock dataset of {len(data)} patients loaded into MongoDB!")
