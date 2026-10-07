import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Load dataset
data = pd.read_csv("data/ai4i2020.csv")

# Select required columns
X = data[
    [
        "Type",
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]"
    ]
].copy()

y = data["Machine failure"]

# Convert machine type into numbers
X["Type"] = X["Type"].map({
    "L": 0,
    "M": 1,
    "H": 2
})

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Train Logistic Regression
model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

# Check accuracy
accuracy = model.score(X_test, y_test)

print("Model trained successfully!")
print("Accuracy:", round(accuracy * 100, 2), "%")

# Save new model
joblib.dump(model, "models/logistic_model.pkl")

print("New model saved successfully!")