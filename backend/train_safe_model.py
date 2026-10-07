import csv
import math
import json

DATASET = "data/ai4i2020.csv"
MODEL_FILE = "models/safe_model.json"


def sigmoid(z):
    if z < -60:
        return 0.0
    if z > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))


def normalize(value, minimum, maximum):
    if maximum == minimum:
        return 0.0
    return (value - minimum) / (maximum - minimum)


# Load dataset
rows = []

with open(DATASET, "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for row in reader:
        machine_type = row["Type"]

        if machine_type == "L":
            type_value = 0
        elif machine_type == "M":
            type_value = 1
        else:
            type_value = 2

        rows.append({
            "type": type_value,
            "air": float(row["Air temperature [K]"]),
            "process": float(row["Process temperature [K]"]),
            "speed": float(row["Rotational speed [rpm]"]),
            "torque": float(row["Torque [Nm]"]),
            "wear": float(row["Tool wear [min]"]),
            "failure": int(row["Machine failure"])
        })


# Feature ranges
features = ["type", "air", "process", "speed", "torque", "wear"]

ranges = {}

for feature in features:
    values = [row[feature] for row in rows]
    ranges[feature] = {
        "min": min(values),
        "max": max(values)
    }


# Simple logistic model trained with gradient descent
weights = [0.0] * len(features)
bias = 0.0

learning_rate = 0.08
epochs = 1500


for epoch in range(epochs):

    gradients = [0.0] * len(features)
    bias_gradient = 0.0

    for row in rows:

        x = []

        for feature in features:
            x.append(
                normalize(
                    row[feature],
                    ranges[feature]["min"],
                    ranges[feature]["max"]
                )
            )

        z = bias

        for i in range(len(features)):
            z += weights[i] * x[i]

        prediction = sigmoid(z)

        error = prediction - row["failure"]

        for i in range(len(features)):
            gradients[i] += error * x[i]

        bias_gradient += error

    n = len(rows)

    for i in range(len(features)):
        weights[i] -= learning_rate * gradients[i] / n

    bias -= learning_rate * bias_gradient / n


model = {
    "features": features,
    "weights": weights,
    "bias": bias,
    "ranges": ranges
}


with open(MODEL_FILE, "w", encoding="utf-8") as file:
    json.dump(model, file, indent=4)


print("SAFE MODEL CREATED")
print("Training rows:", len(rows))
print("Model file:", MODEL_FILE)