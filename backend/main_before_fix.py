from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import mysql.connector


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Predictive Maintenance API",
    description="AI-based machine failure prediction system",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Load trained Random Forest model
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(
    BASE_DIR,
    "models",
    "random_forest_model.pkl"
)

model = joblib.load(model_path)


# --------------------------------------------------
# MySQL Database Connection
# --------------------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MySQL@12345",
        database="predictive_maintenance"
    )


# --------------------------------------------------
# Input data structure
# --------------------------------------------------

class MachineData(BaseModel):
    machine_type: str
    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float


# --------------------------------------------------
# Home API
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Predictive Maintenance API is running"
    }


# --------------------------------------------------
# Prediction API
# --------------------------------------------------

@app.post("/predict")
def predict(data: MachineData):

    # Convert machine type into model format
    type_l = 1 if data.machine_type.upper() == "L" else 0
    type_m = 1 if data.machine_type.upper() == "M" else 0

    # Create input DataFrame
    input_data = pd.DataFrame([{
        "Air temperature [K]": data.air_temperature,
        "Process temperature [K]": data.process_temperature,
        "Rotational speed [rpm]": data.rotational_speed,
        "Torque [Nm]": data.torque,
        "Tool wear [min]": data.tool_wear,
        "Type_L": type_l,
        "Type_M": type_m
    }])

    # Make prediction
    prediction = model.predict(input_data)[0]

    # Get failure probability
    probability = model.predict_proba(input_data)[0][1]

    # Convert probability to percentage
    failure_probability = round(probability * 100, 2)

    # Determine status
    if prediction == 1:
        status = "Failure Risk"
        message = "Machine may require maintenance inspection."
    else:
        status = "Normal"
        message = "Machine is operating within the learned normal pattern."

    # --------------------------------------------------
    # Save prediction to MySQL
    # --------------------------------------------------

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO machine_data
        (
            machine_type,
            air_temperature,
            process_temperature,
            rotational_speed,
            torque,
            tool_wear,
            failure_prediction,
            failure_probability
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data.machine_type.upper(),
        data.air_temperature,
        data.process_temperature,
        data.rotational_speed,
        data.torque,
        data.tool_wear,
        status,
        failure_probability
    )

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()

    # --------------------------------------------------
    # Return result
    # --------------------------------------------------

    return {
        "prediction": int(prediction),
        "status": status,
        "failure_probability": failure_probability,
        "message": message,
        "database_status": "Prediction saved successfully"
    }

# Dashboard Statistics
@app.get("/dashboard")
def dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            COUNT(*) AS total_predictions,
            SUM(CASE WHEN failure_prediction = 'Normal' THEN 1 ELSE 0 END) AS normal_machines,
            SUM(CASE WHEN failure_prediction = 'Failure Risk' THEN 1 ELSE 0 END) AS failure_risk,
            ROUND(AVG(failure_probability), 2) AS average_probability
        FROM machine_data
    """)

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "total_predictions": result["total_predictions"] or 0,
        "normal_machines": result["normal_machines"] or 0,
        "failure_risk": result["failure_risk"] or 0,
        "average_probability": result["average_probability"] or 0
    }

# Prediction History
@app.get("/history")
def prediction_history():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            machine_type,
            air_temperature,
            process_temperature,
            rotational_speed,
            torque,
            tool_wear,
            failure_prediction,
            failure_probability,
            created_at
        FROM machine_data
        ORDER BY id DESC
        LIMIT 10
    """)

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return history