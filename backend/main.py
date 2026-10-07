from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import math
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


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://predictive-maintenance-frontend-9bl6.onrender.com",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Load Safe AI Model
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

model_path = os.path.join(
    BASE_DIR,
    "models",
    "safe_model.json"
)

with open(model_path, "r", encoding="utf-8") as file:
    safe_model = json.load(file)


# --------------------------------------------------
# Temporary in-memory storage
# Used when MySQL is unavailable
# --------------------------------------------------

memory_history = []


# --------------------------------------------------
# Safe Prediction Function
# --------------------------------------------------

def safe_predict(data):

    machine_type = data.machine_type.upper()

    if machine_type == "L":
        type_value = 0

    elif machine_type == "M":
        type_value = 1

    elif machine_type == "H":
        type_value = 2

    else:
        raise ValueError(
            "Machine type must be L, M, or H"
        )

    values = {
        "type": type_value,
        "air": data.air_temperature,
        "process": data.process_temperature,
        "speed": data.rotational_speed,
        "torque": data.torque,
        "wear": data.tool_wear
    }

    # Normalize input values
    x = []

    for feature in safe_model["features"]:

        minimum = safe_model["ranges"][feature]["min"]
        maximum = safe_model["ranges"][feature]["max"]

        if maximum == minimum:

            normalized_value = 0.0

        else:

            normalized_value = (
                values[feature] - minimum
            ) / (maximum - minimum)

        x.append(normalized_value)

    # Calculate model score
    z = safe_model["bias"]

    for i in range(len(x)):
        z += safe_model["weights"][i] * x[i]

    # Prevent overflow
    z = max(min(z, 60), -60)

    # Sigmoid probability
    probability = 1 / (1 + math.exp(-z))

    failure_probability = round(
        probability * 100,
        2
    )

    # Classification
    prediction = 1 if probability >= 0.5 else 0

    return prediction, failure_probability


# --------------------------------------------------
# MySQL Database Connection
# --------------------------------------------------

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv(
            "MYSQL_HOST",
            "localhost"
        ),

        user=os.getenv(
            "MYSQL_USER",
            "root"
        ),

        password=os.getenv(
            "MYSQL_PASSWORD",
            "MySQL@12345"
        ),

        database=os.getenv(
            "MYSQL_DATABASE",
            "predictive_maintenance"
        )
    )


# --------------------------------------------------
# Input Data Structure
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
        "message": "Predictive Maintenance API is running",
        "status": "online"
    }


# --------------------------------------------------
# Health Check API
# --------------------------------------------------

@app.get("/health")
def health():

    database_status = "unavailable"

    try:

        connection = get_db_connection()

        if connection.is_connected():
            database_status = "connected"

        connection.close()

    except Exception:

        database_status = "unavailable"

    return {
        "api": "online",
        "database": database_status
    }


# --------------------------------------------------
# Prediction API
# --------------------------------------------------

@app.post("/predict")
def predict(data: MachineData):

    # --------------------------------------------------
    # AI prediction
    # --------------------------------------------------

    try:

        prediction, failure_probability = safe_predict(data)

    except ValueError as error:

        return {
            "error": str(error)
        }


    # --------------------------------------------------
    # Determine status
    # --------------------------------------------------

    if prediction == 1:

        status = "Failure Risk"

        message = (
            "Machine may require maintenance inspection."
        )

    else:

        status = "Normal"

        message = (
            "Machine is operating within the learned normal pattern."
        )


    # --------------------------------------------------
    # Create history record
    # --------------------------------------------------

    history_record = {

        "machine_type":
            data.machine_type.upper(),

        "air_temperature":
            data.air_temperature,

        "process_temperature":
            data.process_temperature,

        "rotational_speed":
            data.rotational_speed,

        "torque":
            data.torque,

        "tool_wear":
            data.tool_wear,

        "failure_prediction":
            status,

        "failure_probability":
            failure_probability
    }


    # --------------------------------------------------
    # Save to database
    # --------------------------------------------------

    database_status = (
        "Prediction generated successfully"
    )

    try:

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

        cursor.execute(
            query,
            values
        )

        connection.commit()

        cursor.close()

        connection.close()

        database_status = (
            "Prediction saved successfully"
        )

    except Exception:

        # Database unavailable.
        # Keep prediction working.

        memory_history.insert(
            0,
            history_record
        )

        database_status = (
            "Prediction generated; database unavailable"
        )


    # --------------------------------------------------
    # Return Result
    # --------------------------------------------------

    return {

        "prediction":
            int(prediction),

        "status":
            status,

        "failure_probability":
            failure_probability,

        "message":
            message,

        "database_status":
            database_status
    }


# --------------------------------------------------
# Dashboard Statistics
# --------------------------------------------------

@app.get("/dashboard")
def dashboard():

    # --------------------------------------------------
    # Try MySQL first
    # --------------------------------------------------

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT

                COUNT(*) AS total_predictions,

                SUM(
                    CASE
                        WHEN failure_prediction = 'Normal'
                        THEN 1
                        ELSE 0
                    END
                ) AS normal_machines,

                SUM(
                    CASE
                        WHEN failure_prediction = 'Failure Risk'
                        THEN 1
                        ELSE 0
                    END
                ) AS failure_risk,

                ROUND(
                    AVG(failure_probability),
                    2
                ) AS average_probability

            FROM machine_data
        """)

        result = cursor.fetchone()

        cursor.close()

        connection.close()


        return {

            "total_predictions":
                result["total_predictions"] or 0,

            "normal_machines":
                result["normal_machines"] or 0,

            "failure_risk":
                result["failure_risk"] or 0,

            "average_probability":
                result["average_probability"] or 0
        }


    except Exception:

        # --------------------------------------------------
        # Use memory data if MySQL unavailable
        # --------------------------------------------------

        total_predictions = len(
            memory_history
        )

        normal_machines = sum(
            1
            for item in memory_history
            if item["failure_prediction"] == "Normal"
        )

        failure_risk = sum(
            1
            for item in memory_history
            if item["failure_prediction"] == "Failure Risk"
        )

        if total_predictions > 0:

            average_probability = round(
                sum(
                    item["failure_probability"]
                    for item in memory_history
                ) / total_predictions,
                2
            )

        else:

            average_probability = 0


        return {

            "total_predictions":
                total_predictions,

            "normal_machines":
                normal_machines,

            "failure_risk":
                failure_risk,

            "average_probability":
                average_probability
        }


# --------------------------------------------------
# Prediction History
# --------------------------------------------------

@app.get("/history")
def prediction_history():

    # --------------------------------------------------
    # Try MySQL first
    # --------------------------------------------------

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

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


    except Exception:

        # --------------------------------------------------
        # Use memory history if MySQL unavailable
        # --------------------------------------------------

        return memory_history[:10]