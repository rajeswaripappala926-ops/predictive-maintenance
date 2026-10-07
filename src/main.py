import joblib
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# =========================================================
# 1. LOAD DATASET
# =========================================================

# Project folder path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset path
data_path = os.path.join(BASE_DIR, "data", "ai4i2020.csv")

# Read dataset
data = pd.read_csv(data_path)

print("\n======================================")
print("PREDICTIVE MAINTENANCE PROJECT")
print("======================================")

print("\nDataset loaded successfully!")
print("Dataset shape:", data.shape)


# =========================================================
# 2. UNDERSTAND THE DATA
# =========================================================

print("\nFirst 5 rows:")
print(data.head())

print("\nColumn names:")
print(data.columns.tolist())

print("\nDataset information:")
print(data.info())

print("\nMissing values:")
print(data.isnull().sum())

print("\nStatistical summary:")
print(data.describe())


# =========================================================
# 3. CHECK MACHINE FAILURE
# =========================================================

print("\nMachine Failure Count:")
print(data["Machine failure"].value_counts())

print("\nMachine Failure Percentage:")
print(data["Machine failure"].value_counts(normalize=True) * 100)


# =========================================================
# 4. REMOVE UNNECESSARY COLUMNS
# =========================================================

# UDI and Product ID are identifiers.
# Failure-mode columns can leak information about the target,
# so we don't use them as prediction features.

columns_to_drop = [
    "UDI",
    "Product ID",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF"
]

data = data.drop(columns=columns_to_drop)

print("\nColumns after removing unnecessary columns:")
print(data.columns.tolist())


# =========================================================
# 5. DATA CLEANING
# =========================================================

print("\nMissing values after cleaning:")
print(data.isnull().sum())

# Remove duplicate rows if any
duplicate_count = data.duplicated().sum()

print("\nDuplicate rows:", duplicate_count)

if duplicate_count > 0:
    data = data.drop_duplicates()

print("Dataset shape after cleaning:", data.shape)


# =========================================================
# 6. EXPLORATORY DATA ANALYSIS
# =========================================================

# Machine failure distribution

plt.figure(figsize=(6, 4))

sns.countplot(
    data=data,
    x="Machine failure"
)

plt.title("Machine Failure Distribution")
plt.xlabel("Machine Failure (0 = Normal, 1 = Failure)")
plt.ylabel("Number of Machines")

plt.tight_layout()
plt.show()


# =========================================================
# 7. TEMPERATURE ANALYSIS
# =========================================================

plt.figure(figsize=(7, 5))

sns.boxplot(
    data=data,
    x="Machine failure",
    y="Air temperature [K]"
)

plt.title("Air Temperature vs Machine Failure")
plt.xlabel("Machine Failure")
plt.ylabel("Air Temperature [K]")

plt.tight_layout()
plt.show()


# =========================================================
# 8. TORQUE ANALYSIS
# =========================================================

plt.figure(figsize=(7, 5))

sns.boxplot(
    data=data,
    x="Machine failure",
    y="Torque [Nm]"
)

plt.title("Torque vs Machine Failure")
plt.xlabel("Machine Failure")
plt.ylabel("Torque [Nm]")

plt.tight_layout()
plt.show()


# =========================================================
# 9. ROTATIONAL SPEED ANALYSIS
# =========================================================

plt.figure(figsize=(7, 5))

sns.boxplot(
    data=data,
    x="Machine failure",
    y="Rotational speed [rpm]"
)

plt.title("Rotational Speed vs Machine Failure")
plt.xlabel("Machine Failure")
plt.ylabel("Rotational Speed [rpm]")

plt.tight_layout()
plt.show()


# =========================================================
# 10. TOOL WEAR ANALYSIS
# =========================================================

plt.figure(figsize=(7, 5))

sns.boxplot(
    data=data,
    x="Machine failure",
    y="Tool wear [min]"
)

plt.title("Tool Wear vs Machine Failure")
plt.xlabel("Machine Failure")
plt.ylabel("Tool Wear [min]")

plt.tight_layout()
plt.show()


# =========================================================
# 11. CORRELATION HEATMAP
# =========================================================

numeric_data = data.select_dtypes(include="number")

plt.figure(figsize=(10, 7))

sns.heatmap(
    numeric_data.corr(),
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("Correlation Heatmap")

plt.tight_layout()
plt.show()


# =========================================================
# 12. SELECT FEATURES AND TARGET
# =========================================================

features = [
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]"
]

target = "Machine failure"

X = data[features]
y = data[target]


print("\nFeatures used for prediction:")
print(features)

print("\nTarget:")
print(target)


# =========================================================
# 13. CONVERT TYPE INTO NUMERICAL VALUES
# =========================================================

# Machine Type contains categories such as L, M and H.
# Machine learning models require numerical values.

X = pd.get_dummies(
    X,
    columns=["Type"],
    drop_first=True,
    dtype=int
)

print("\nFeatures after encoding:")
print(X.head())

print("\nFeature columns:")
print(X.columns.tolist())


# =========================================================
# 14. TRAIN TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining data size:", X_train.shape)
print("Testing data size:", X_test.shape)


# =========================================================
# 15. LOGISTIC REGRESSION
# =========================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

logistic_model = LogisticRegression(
    class_weight="balanced",
    random_state=42,
    max_iter=1000
)

logistic_model.fit(
    X_train_scaled,
    y_train
)

logistic_predictions = logistic_model.predict(
    X_test_scaled
)


# =========================================================
# 16. RANDOM FOREST
# =========================================================

random_forest_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

random_forest_model.fit(
    X_train,
    y_train
)

random_forest_predictions = random_forest_model.predict(
    X_test
)


# =========================================================
# 17. MODEL EVALUATION FUNCTION
# =========================================================

def evaluate_model(model_name, y_true, y_pred):

    print("\n======================================")
    print(model_name)
    print("======================================")

    accuracy = accuracy_score(y_true, y_pred)

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    print("Accuracy :", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall   :", round(recall, 4))
    print("F1 Score :", round(f1, 4))

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            zero_division=0
        )
    )

    print("Confusion Matrix:")
    print(
        confusion_matrix(
            y_true,
            y_pred
        )
    )


# =========================================================
# 18. EVALUATE LOGISTIC REGRESSION
# =========================================================

evaluate_model(
    "LOGISTIC REGRESSION",
    y_test,
    logistic_predictions
)


# =========================================================
# 19. EVALUATE RANDOM FOREST
# =========================================================

evaluate_model(
    "RANDOM FOREST",
    y_test,
    random_forest_predictions
)


# =========================================================
# 20. RANDOM FOREST FEATURE IMPORTANCE
# =========================================================

feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": random_forest_model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="Importance",
    ascending=False
)

print("\n======================================")
print("FEATURE IMPORTANCE")
print("======================================")

print(feature_importance)


# Plot feature importance

plt.figure(figsize=(9, 6))

sns.barplot(
    data=feature_importance,
    x="Importance",
    y="Feature"
)

plt.title("Random Forest Feature Importance")
plt.xlabel("Importance")
plt.ylabel("Feature")

plt.tight_layout()
plt.show()


# =========================================================
# 21. SAMPLE MACHINE PREDICTION
# =========================================================

sample_machine = pd.DataFrame({
    "Type": ["M"],
    "Air temperature [K]": [300],
    "Process temperature [K]": [310],
    "Rotational speed [rpm]": [1500],
    "Torque [Nm]": [50],
    "Tool wear [min]": [180]
})


# Convert Type into the same format as training data

sample_machine = pd.get_dummies(
    sample_machine,
    columns=["Type"],
    drop_first=True,
    dtype=int
)


# Make sure sample has exactly the same columns as training data

sample_machine = sample_machine.reindex(
    columns=X.columns,
    fill_value=0
)


# Predict

sample_prediction = random_forest_model.predict(
    sample_machine
)


# Probability

sample_probability = random_forest_model.predict_proba(
    sample_machine
)[0][1]


print("\n======================================")
print("SAMPLE MACHINE PREDICTION")
print("======================================")

print("Machine Input:")
print(sample_machine)

print("\nFailure Probability:",
      round(sample_probability * 100, 2), "%")


if sample_prediction[0] == 1:

    print("\nPrediction: ⚠️ MACHINE FAILURE RISK")

else:

    print("\nPrediction: ✅ MACHINE NORMAL")


print("\n======================================")
print("PROJECT COMPLETED SUCCESSFULLY")
print("======================================")

# =========================================================
# 22. SAVE TRAINED MODEL
# =========================================================

model_path = os.path.join(
    BASE_DIR,
    "models",
    "random_forest_model.pkl"
)

joblib.dump(
    random_forest_model,
    model_path
)

print("\nRandom Forest model saved successfully!")
print("Model location:", model_path)