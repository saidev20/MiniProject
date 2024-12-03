import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['nutritionist_app']
patients_collection = db['patients']

# Fetch data from MongoDB
def fetch_data():
    patients_data = list(patients_collection.find({}, {"_id": 0}))
    
    processed_data = []
    labels = []

    for patient in patients_data:
        try:
            # Extract relevant data
            glucose = patient["blood_metrics"]["glucose_levels"]["FBPS"]
            PPBS = patient["blood_metrics"]["glucose_levels"]["PPBS"]
            HbA1c = patient["blood_metrics"]["HbA1c"]
            LDL = patient["blood_metrics"]["cholesterol"]["LDL"]
            HDL = patient["blood_metrics"]["cholesterol"]["HDL"]
            triglycerides = patient["blood_metrics"]["cholesterol"]["triglycerides"]
            BMI = patient["BMI"]
            physical_activity = patient["physical_activity"]
            diet_type = patient.get("diet_type")  # Use .get() to avoid KeyError if diet_type is missing
            
            # Only process patients with all necessary data
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

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(
    processed_data, 
    columns=["FBPS", "PPBS", "HbA1c", "LDL", "HDL", "triglycerides", "BMI", "physical_activity"]
)
labels = pd.Series(labels)

# Encode the 'physical_activity' column
activity_mapping = {"low": 1, "moderate": 2, "high": 3}
df["physical_activity"] = df["physical_activity"].map(activity_mapping)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df, labels, test_size=0.2, random_state=42)

# Initialize and train the Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Save the trained model to a file
joblib.dump(model, "diet_model.pkl")
print("Model saved as diet_model.pkl")
