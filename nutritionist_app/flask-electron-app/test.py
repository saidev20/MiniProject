import joblib
model = joblib.load("diet_model.pkl")
feature_importance = model.feature_importances_
feature_names = ["FBPS", "PPBS", "HbA1c", "LDL", "HDL", "triglycerides", "BMI", "physical_activity"]
for name, importance in zip(feature_names, feature_importance):
    print(f"{name}: {importance:.2f}")
