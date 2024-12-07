from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['nutritionist_app']
collection = db['patients']

# Accurate classification function
def classify_diet_type(metrics):
    FBPS = metrics["glucose_levels"]["FBPS"]
    PPBS = metrics["glucose_levels"]["PPBS"]
    HbA1c = metrics["HbA1c"]
    LDL = metrics["cholesterol"]["LDL"]
    BMI = metrics["BMI"]
    physical_activity = metrics["physical_activity"]

    # Classify based on glucose levels
    if FBPS >= 126 or PPBS >= 200 or HbA1c >= 6.5:
        return "low-carb"  # For diabetes management
    elif LDL > 130 or BMI > 25:
        return "low-fat"  # For cholesterol or obesity
    elif physical_activity == "high" and HbA1c < 6.5:
        return "high-protein"  # For active individuals with normal glucose levels
    else:
        return "balanced"  # Default recommendation

# Generate diabetic patient data
data = []
for i in range(1000):
    # Generate FBS and PPBS in diabetic range
    FBS = 126 + (i % 50)  # Diabetic FBS: ≥126
    PPBS = FBS + 80 + (i % 40)  # Ensure PPBS ≥200 and represents realistic postprandial spikes

    # Generate other diabetic-specific metrics
    HbA1c = round(6.5 + (i % 20) / 10, 1)  # HbA1c ≥6.5
    LDL = 100 + (i % 70)  # LDL cholesterol in realistic ranges
    HDL = 35 + (i % 25)  # HDL cholesterol
    triglycerides = 150 + (i % 100)  # Higher triglyceride levels
    BMI = round(25 + (i % 15) * 0.5, 1)  # Overweight or obese BMI range: ≥25
    physical_activity = "low" if i % 3 == 0 else "moderate" if i % 2 == 0 else "high"

    # Construct patient record
    patient = {
        "name": f"Patient {i + 1}",
        "BMI": BMI,
        "blood_metrics": {
            "glucose_levels": {"FBPS": FBS, "PPBS": PPBS},
            "HbA1c": HbA1c,
            "cholesterol": {"LDL": LDL, "HDL": HDL, "triglycerides": triglycerides},
        },
        "physical_activity": physical_activity,
        "diet_type": None,  # Placeholder for diet type
    }

    # Classify diet type
    patient["diet_type"] = classify_diet_type({
        "glucose_levels": patient["blood_metrics"]["glucose_levels"],
        "HbA1c": patient["blood_metrics"]["HbA1c"],
        "cholesterol": patient["blood_metrics"]["cholesterol"],
        "BMI": patient["BMI"],
        "physical_activity": patient["physical_activity"],
    })

    data.append(patient)

# Insert refined data into MongoDB
collection.drop()  # Clean previous data
result = collection.insert_many(data)
print(f"{len(result.inserted_ids)} diabetic patient records inserted successfully into MongoDB!")
