import random
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['nutritionist_app']
collection = db['patients']

# Classification function
def classify_diet_type_weighted(metrics):
    results = {"low-carb": 0, "low-fat": 0, "high-protein": 0, "balanced": 0}
    # Low-carb conditions
    if metrics["glucose_levels"]["FBPS"] >= 126 or metrics["glucose_levels"]["PPBS"] >= 200:
        results["low-carb"] += 5
    if metrics["HbA1c"] >= 6.5:
        results["low-carb"] += 3
    # Low-fat conditions
    if metrics["cholesterol"]["LDL"] > 130:
        results["low-fat"] += 4
    if metrics["cholesterol"]["HDL"] < 40 or metrics["cholesterol"]["triglycerides"] > 150:
        results["low-fat"] += 3
    if metrics["BMI"] >= 25:
        results["low-fat"] += 2
    # High-protein conditions
    if metrics["physical_activity"] >= 4:
        results["high-protein"] += 5
    if metrics["HbA1c"] < 5.7 and metrics["glucose_levels"]["FBPS"] < 100:
        results["high-protein"] += 3
    # Balanced conditions
    if metrics["physical_activity"] >= 3 and metrics["BMI"] < 25:
        results["balanced"] += 4
    if metrics["cholesterol"]["LDL"] < 130 and metrics["glucose_levels"]["FBPS"] < 100:
        results["balanced"] += 2
    return max(results, key=results.get)

# Fetch and prepare data from MongoDB
def fetch_data():
    patients_data = list(collection.find({}, {"_id": 0}))

    processed_data = []
    labels = []

    for patient in patients_data:
        try:
            glucose = patient["blood_metrics"]["glucose_levels"]["FBPS"]
            PPBS = patient["blood_metrics"]["glucose_levels"]["PPBS"]
            HbA1c = patient["blood_metrics"]["HbA1c"]
            LDL = patient["blood_metrics"]["cholesterol"]["LDL"]
            HDL = patient["blood_metrics"]["cholesterol"]["HDL"]
            triglycerides = patient["blood_metrics"]["cholesterol"]["triglycerides"]
            BMI = patient["BMI"]
            physical_activity = patient["physical_activity"]
            diet_type = patient.get("diet_type")

            if None not in (glucose, PPBS, HbA1c, LDL, HDL, triglycerides, BMI, physical_activity, diet_type):
                processed_data.append([glucose, PPBS, HbA1c, LDL, HDL, triglycerides, BMI, physical_activity])
                labels.append(diet_type)
        except KeyError as e:
            print(f"Missing key {e} in patient record: {patient}")

    return processed_data, labels

# Fetch and prepare data
processed_data, labels = fetch_data()

if not processed_data or not labels:
    print("No valid data found for training.")
    exit()

df = pd.DataFrame(processed_data, columns=["FBPS", "PPBS", "HbA1c", "LDL", "HDL", "triglycerides", "BMI", "physical_activity"])
labels = pd.Series(labels)


# Analyze the distribution of diet types
print(labels.value_counts())
# Increase HbA1c's weight significantly by multiplying it by a factor of 50
df["HbA1c_weighted"] = df["HbA1c"] * 50  # Much stronger influence
df = df.drop(columns=["HbA1c"])  # Remove original HbA1c to avoid redundancy

# Decrease LDL's importance by dividing by 5 to reduce its weight
df["LDL_reduced"] = df["LDL"] / 5  # Decrease LDL's weight
df = df.drop(columns=["LDL"])  # Remove original LDL to avoid redundancy

# Adjust feature scaling for the model
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, labels, test_size=0.2, random_state=42)

# Train the RandomForest model with hyperparameter tuning
model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Evaluate Feature Importances
importances = model.feature_importances_
feature_names = df.columns
importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

print("\nFeature Importances:")
print(importance_df)

# Evaluate accuracy
accuracy = accuracy_score(y_test, model.predict(X_test))
print("Model Accuracy:", accuracy)

# Save the trained model to a file
joblib.dump(model, "diet_model2.pkl")
print("Model saved as diet_model2.pkl")
