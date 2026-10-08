from fastapi.middleware.cors import CORSMiddleware 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import math
import os
import mysql.connector

app = FastAPI(
    title="Predictive Maintenance API",
    description="AI-based machine failure prediction system",
    version="1.0"
)

# CORS
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Project path
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Load safe model
model_path = os.path.join(
    BASE_DIR,
    "models",
    "safe_model.json"
)

with open(model_path, "r", encoding="utf-8") as file:
    safe_model = json.load(file)

memory_history = []


# -----------------------------
# AI Prediction
# -----------------------------

def safe_predict(data):
    machine_type = data.machine_type.upper()

    if machine_type == "L":
        type_value = 0
    elif machine_type == "M":
        type_value = 1
    elif machine_type == "H":
        type_value = 2
    else:
        raise ValueError("Machine type must be L, M, or H")

    values = {
        "type": type_value,
        "air": data.air_temperature,
        "process": data.process_temperature,
        "speed": data.rotational_speed,
        "torque": data.torque,
        "wear": data.tool_wear
    }

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

    z = safe_model["bias"]

    for i in range(len(x)):
        z += safe_model["weights"][i] * x[i]

    z = max(min(z, 60), -60)

    probability = 1 / (1 + math.exp(-z))

    failure_probability = round(
        probability * 100,
        2
    )

    prediction = 1 if probability >= 0.5 else 0

    return prediction, failure_probability


# -----------------------------
# Risk Level
# -----------------------------

def calculate_risk_level(failure_probability):

    if failure_probability < 30:
        return "LOW"

    if failure_probability < 70:
        return "MEDIUM"

    return "HIGH"


# -----------------------------
# Health Score
# -----------------------------

def calculate_health_score(failure_probability):

    score = 100 - failure_probability

    score = max(0, min(100, score))

    return round(score, 2)


# -----------------------------
# Maintenance Recommendation
# -----------------------------

def get_maintenance_recommendation(
    risk_level,
    tool_wear,
    torque,
    rotational_speed,
    air_temperature,
    process_temperature
):

    recommendations = []

    if risk_level == "HIGH":
        recommendations.append(
            "Immediate maintenance inspection recommended."
        )

    elif risk_level == "MEDIUM":
        recommendations.append(
            "Schedule maintenance inspection soon."
        )

    else:
        recommendations.append(
            "Machine condition is healthy. Continue monitoring."
        )

    if tool_wear >= 200:
        recommendations.append(
            "Inspect or replace the cutting tool."
        )

    elif tool_wear >= 150:
        recommendations.append(
            "Monitor tool wear closely."
        )

    if torque >= 60:
        recommendations.append(
            "Check machine load and torque levels."
        )

    elif torque >= 50:
        recommendations.append(
            "Monitor torque for abnormal increases."
        )

    temperature_difference = (
        process_temperature - air_temperature
    )

    if temperature_difference >= 12:
        recommendations.append(
            "Inspect cooling system and temperature control."
        )

    if rotational_speed >= 2000:
        recommendations.append(
            "Check rotational speed and machine vibration."
        )

    elif rotational_speed <= 1000:
        recommendations.append(
            "Check whether the machine is operating at the required speed."
        )

    return recommendations


# -----------------------------
# Risk Explanation
# -----------------------------

def get_risk_explanation(
    failure_probability,
    tool_wear,
    torque,
    rotational_speed,
    air_temperature,
    process_temperature
):

    factors = []

    if tool_wear >= 200:
        factors.append("high tool wear")

    elif tool_wear >= 150:
        factors.append("elevated tool wear")

    if torque >= 60:
        factors.append("high torque")

    elif torque >= 50:
        factors.append("elevated torque")

    if rotational_speed >= 2000:
        factors.append("high rotational speed")

    elif rotational_speed <= 1000:
        factors.append("low rotational speed")

    temperature_difference = (
        process_temperature - air_temperature
    )

    if temperature_difference >= 12:
        factors.append("high temperature difference")

    if len(factors) == 0:

        if failure_probability < 30:
            return (
                "Sensor values are currently within a "
                "stable operating pattern."
            )

        return (
            "The model has identified an increased "
            "probability of machine failure."
        )

    return "Risk indicators detected: " + ", ".join(factors) + "."


# -----------------------------
# Machine Analysis
# -----------------------------

def build_machine_analysis(
    failure_probability,
    tool_wear,
    torque,
    rotational_speed,
    air_temperature,
    process_temperature
):

    risk_level = calculate_risk_level(
        failure_probability
    )

    health_score = calculate_health_score(
        failure_probability
    )

    maintenance_actions = get_maintenance_recommendation(
        risk_level,
        tool_wear,
        torque,
        rotational_speed,
        air_temperature,
        process_temperature
    )

    risk_explanation = get_risk_explanation(
        failure_probability,
        tool_wear,
        torque,
        rotational_speed,
        air_temperature,
        process_temperature
    )

    return {
        "risk_level": risk_level,
        "health_score": health_score,
        "maintenance_recommendation": maintenance_actions[0],
        "maintenance_actions": maintenance_actions,
        "risk_explanation": risk_explanation
    }


# -----------------------------
# MySQL Connection
# -----------------------------

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "MySQL@12345"),
        database=os.getenv(
            "MYSQL_DATABASE",
            "predictive_maintenance"
        )
    )


# -----------------------------
# Input Model
# -----------------------------

class MachineData(BaseModel):

    machine_type: str
    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float


# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "Predictive Maintenance API is running",
        "status": "online"
    }


# -----------------------------
# Health
# -----------------------------

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


# -----------------------------
# Prediction
# -----------------------------

@app.post("/predict")
def predict(data: MachineData):

    try:

        prediction, failure_probability = safe_predict(data)

    except ValueError as error:

        return {
            "error": str(error)
        }

    if prediction == 1:

        status = "Failure Risk"

        message = (
            "Machine may require maintenance inspection."
        )

    else:

        status = "Normal"

        message = (
            "Machine is operating within the learned "
            "normal pattern."
        )

    analysis = build_machine_analysis(
        failure_probability,
        data.tool_wear,
        data.torque,
        data.rotational_speed,
        data.air_temperature,
        data.process_temperature
    )

    history_record = {
        "machine_type": data.machine_type.upper(),
        "air_temperature": data.air_temperature,
        "process_temperature": data.process_temperature,
        "rotational_speed": data.rotational_speed,
        "torque": data.torque,
        "tool_wear": data.tool_wear,
        "failure_prediction": status,
        "failure_probability": failure_probability,
        "risk_level": analysis["risk_level"],
        "health_score": analysis["health_score"],
        "maintenance_recommendation": analysis[
            "maintenance_recommendation"
        ],
        "risk_explanation": analysis[
            "risk_explanation"
        ]
    }

    database_status = "Prediction generated successfully"

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

        cursor.execute(query, values)

        connection.commit()

        cursor.close()

        connection.close()

        database_status = "Prediction saved successfully"

    except Exception:

        memory_history.insert(
            0,
            history_record
        )

        database_status = (
            "Prediction generated; database unavailable"
        )

    return {
        "prediction": int(prediction),
        "status": status,
        "failure_probability": failure_probability,
        "risk_level": analysis["risk_level"],
        "health_score": analysis["health_score"],
        "maintenance_recommendation": analysis[
            "maintenance_recommendation"
        ],
        "maintenance_actions": analysis[
            "maintenance_actions"
        ],
        "risk_explanation": analysis[
            "risk_explanation"
        ],
        "message": message,
        "database_status": database_status
    }


# -----------------------------
# Dashboard
# -----------------------------

@app.get("/dashboard")
def dashboard():

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

        total_predictions = len(memory_history)

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
            "total_predictions": total_predictions,
            "normal_machines": normal_machines,
            "failure_risk": failure_risk,
            "average_probability": average_probability
        }


# -----------------------------
# History
# -----------------------------

@app.get("/history")
def prediction_history():

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

        enhanced_history = []

        for item in history:

            analysis = build_machine_analysis(
                item["failure_probability"],
                item["tool_wear"],
                item["torque"],
                item["rotational_speed"],
                item["air_temperature"],
                item["process_temperature"]
            )

            item["risk_level"] = analysis["risk_level"]

            item["health_score"] = analysis["health_score"]

            item["maintenance_recommendation"] = (
                analysis["maintenance_recommendation"]
            )

            item["risk_explanation"] = (
                analysis["risk_explanation"]
            )

            enhanced_history.append(item)

        return enhanced_history

    except Exception:

        return memory_history[:10]