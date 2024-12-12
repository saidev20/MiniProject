import random
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['nutritionist_app']
collection = db['patients']

# Classification function (we'll ensure 500 cases per diet type)
def classify_diet_type(metrics):
    # Low-carb: High glucose levels or HbA1c > 6.5
    if metrics["glucose_levels"]["FBPS"] >= 126 or metrics["glucose_levels"]["PPBS"] >= 200 or metrics["HbA1c"] >= 6.5:
        return "low-carb"
    
    # Low-fat: High LDL or bad cholesterol profile (HDL too low or triglycerides high)
    if metrics["cholesterol"]["LDL"] > 130 or metrics["cholesterol"]["HDL"] < 40 or metrics["cholesterol"]["triglycerides"] > 150:
        return "low-fat"
    
    # High-protein: High physical activity and good glucose control (FBPS < 100 and HbA1c < 5.7)
    # Include BMI consideration (active people with a BMI > 25 might need more protein)
    if metrics["physical_activity"] >= 4 and metrics["glucose_levels"]["FBPS"] < 100 and metrics["HbA1c"] < 5.7:
        if metrics["BMI"] > 25:  # More protein for active individuals with higher BMI
            return "high-protein"
    
    # Balanced: Ideal for someone with well-managed blood glucose, cholesterol, and BMI in normal range
    if metrics["glucose_levels"]["FBPS"] < 100 and metrics["HbA1c"] < 6.5 and metrics["cholesterol"]["LDL"] < 130:
        if 18.5 <= metrics["BMI"] < 25:  # Balanced for people with healthy BMI
            return "balanced"
    
    # Default to balanced if no conditions matched
    return "balanced"

# Function to generate specific diet type
def generate_patient_data(diet_type):
    # Generate health metrics based on diet type
    if diet_type == "low-carb":
        FBS = random.randint(126, 180)
        PPBS = FBS + random.randint(-30, 100)
        HbA1c = round(random.uniform(6.5, 8.5), 1)  # HbA1c ≥ 6.5
        LDL = random.randint(100, 150)  # Low to moderate LDL for low-carb
        HDL = random.randint(40, 60)
        triglycerides = random.randint(150, 250)
    elif diet_type == "low-fat":
        FBS = random.randint(100, 180)
        PPBS = FBS + random.randint(-30, 100)
        HbA1c = round(random.uniform(5.5, 8.5), 1)
        LDL = random.randint(130, 160)  # Higher LDL for low-fat
        HDL = random.randint(30, 50)
        triglycerides = random.randint(150, 250)
    elif diet_type == "high-protein":
        FBS = random.randint(80, 120)
        PPBS = FBS + random.randint(-30, 100)
        HbA1c = round(random.uniform(5.5, 6.5), 1)  # HbA1c < 6.5
        LDL = random.randint(90, 130)  # Normal LDL for high-protein
        HDL = random.randint(40, 60)
        triglycerides = random.randint(150, 250)
        physical_activity = random.randint(4, 5)
    else:  # balanced
        FBS = random.randint(80, 100)
        PPBS = FBS + random.randint(-10, 30)
        HbA1c = round(random.uniform(5.5, 6.5), 1)
        LDL = random.randint(90, 130)  # Normal LDL for balanced
        HDL = random.randint(40, 60)
        triglycerides = random.randint(150, 200)

    # Randomly generate BMI and physical activity
    BMI = round(random.uniform(18, 35), 1)  # BMI from normal to obese
    physical_activity = random.randint(1, 5)

    # Construct patient record
    patient = {
        "name": f"Patient {random.randint(1, 10000)}",
        "BMI": BMI,
        "blood_metrics": {
            "glucose_levels": {"FBPS": FBS, "PPBS": PPBS},
            "HbA1c": HbA1c,
            "cholesterol": {"LDL": LDL, "HDL": HDL, "triglycerides": triglycerides},
        },
        "physical_activity": physical_activity,
        "diet_type": diet_type,
    }

    return patient

# Generate 500 records for each diet type
data = []
for diet_type in ["low-carb", "low-fat", "high-protein", "balanced"]:
    for _ in range(500):
        patient = generate_patient_data(diet_type)
        data.append(patient)

# Insert data into MongoDB
collection.drop()  # Clean previous data
result = collection.insert_many(data)
print(f"{len(result.inserted_ids)} diabetic patient records inserted successfully into MongoDB!")
