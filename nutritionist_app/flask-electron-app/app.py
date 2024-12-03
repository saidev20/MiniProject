from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)

# Load the trained model
model = joblib.load("diet_model.pkl")

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
        
        # Debugging: print the data received
        print(data)

        # Define required fields and validate them
        required_fields = ['FBPS', 'PPBS', 'HbA1c', 'LDL', 'HDL', 'triglycerides', 'BMI', 'physical_activity']
        
        # Check if all required fields are present and valid
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'message': f'Missing or invalid value for {field}'}), 400

        # Extract and convert values from the request data
        FBPS = float(data.get('FBPS'))
        PPBS = float(data.get('PPBS'))
        HbA1c = float(data.get('HbA1c'))
        LDL = float(data.get('LDL'))
        HDL = float(data.get('HDL'))
        triglycerides = float(data.get('triglycerides'))
        BMI = float(data.get('BMI'))
        physical_activity = int(data.get('physical_activity'))
        
        # Prepare the data for prediction (the model expects a certain structure)
        input_data = [[FBPS, PPBS, HbA1c, LDL, HDL, triglycerides, BMI, physical_activity]]
        
        # Make prediction
        predicted_diet = model.predict(input_data)[0]

        # Return the prediction as a JSON response
        return jsonify({'predicted_diet': predicted_diet})
    
    except ValueError as ve:
        return jsonify({'message': f'Invalid data format: {str(ve)}'}), 400
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
