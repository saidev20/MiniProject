from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)

# Load the trained model
model = joblib.load("diet_model2.pkl")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['nutritionist_app']
patients_collection = db['patients']

@app.route('/')
def home():
    # Retrieve all patient names from MongoDB collection
    patients = list(patients_collection.find({}, {"_id": 0, "name": 1}))
    return render_template('patient_details.html', patients=patients)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data from the request
        data = request.get_json()

        # Validate required fields
        required_fields = ['FBPS', 'PPBS', 'HbA1c', 'LDL', 'HDL', 'triglycerides', 'BMI', 'physical_activity']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'message': f'Missing or invalid value for {field}'}), 400

        # Extract and convert values
        metrics = {
            "FBPS": float(data['FBPS']),
            "PPBS": float(data['PPBS']),
            "HbA1c": float(data['HbA1c']),
            "LDL": float(data['LDL']),
            "HDL": float(data['HDL']),
            "triglycerides": float(data['triglycerides']),
            "BMI": float(data['BMI']),
            "physical_activity": int(data['physical_activity'])
        }

        # Prepare data for the model
        input_data = [[
            metrics["FBPS"],
            metrics["PPBS"],
            metrics["HbA1c"],
            metrics["LDL"],
            metrics["HDL"],
            metrics["triglycerides"],
            metrics["BMI"],
            metrics["physical_activity"]
        ]]

        # Get prediction from the model
        predicted_diet = model.predict(input_data)[0]

        # Generate reasoning based on model's prediction and input metrics
        reasoning = generate_reasoning(predicted_diet, metrics)

        # Return prediction and reasoning
        return jsonify({
            "predicted_diet": predicted_diet,
            "reasoning": reasoning
        })

    except ValueError as ve:
        return jsonify({'message': f'Invalid data format: {str(ve)}'}), 400
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


def generate_reasoning(predicted_diet, metrics):
    reasoning = []

    if predicted_diet == "low-carb":
        if metrics["FBPS"] >= 126 or metrics["PPBS"] >= 200:
            reasoning.append("High glucose levels suggest a low-carb diet.")
        if metrics["HbA1c"] >= 6.5:
            reasoning.append("Elevated HbA1c indicates improved glucose management is needed.")

    elif predicted_diet == "low-fat":
        if metrics["LDL"] > 130:
            reasoning.append("High LDL cholesterol suggests reducing dietary fat.")
        if metrics["HDL"] < 40 or metrics["triglycerides"] > 150:
            reasoning.append("Low HDL or high triglycerides align with a low-fat diet.")
        if metrics["BMI"] >= 25:
            reasoning.append("Higher BMI suggests reducing calorie intake.")

    elif predicted_diet == "high-protein":
        if metrics["physical_activity"] >= 4:
            reasoning.append("High physical activity aligns with a high-protein diet.")
        if metrics["FBPS"] < 100 and metrics["HbA1c"] < 5.7:
            reasoning.append("Normal glucose levels support protein-rich diets.")

    elif predicted_diet == "balanced":
        if metrics["physical_activity"] >= 3 and metrics["BMI"] < 25:
            reasoning.append("Moderate physical activity and healthy BMI favor a balanced diet.")
        if metrics["LDL"] < 130 and metrics["FBPS"] < 100:
            reasoning.append("Healthy cholesterol and glucose levels align with a balanced diet.")

    # Default reasoning
    if not reasoning:
        reasoning.append("Prediction is based on overall health metrics.")

    return reasoning


if __name__ == '__main__':
    app.run(debug=True)
