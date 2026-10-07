import streamlit as st
import pandas as pd
import joblib
import os


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Predictive Maintenance",
    page_icon="⚙️",
    layout="wide"
)


# =========================================================
# 2. LOAD TRAINED MODEL
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(
    BASE_DIR,
    "models",
    "random_forest_model.pkl"
)

model = joblib.load(model_path)


# =========================================================
# 3. TITLE
# =========================================================

st.title("⚙️ AI-Based Predictive Maintenance System")

st.write(
    "Predict whether an industrial machine is likely to fail "
    "based on its operating conditions."
)

st.divider()


# =========================================================
# 4. SIDEBAR
# =========================================================

st.sidebar.header("Machine Information")

machine_type = st.sidebar.selectbox(
    "Machine Type",
    ["L", "M", "H"]
)

air_temperature = st.sidebar.number_input(
    "Air Temperature [K]",
    min_value=295.0,
    max_value=305.0,
    value=300.0,
    step=0.1
)

process_temperature = st.sidebar.number_input(
    "Process Temperature [K]",
    min_value=305.0,
    max_value=314.0,
    value=310.0,
    step=0.1
)

rotational_speed = st.sidebar.number_input(
    "Rotational Speed [rpm]",
    min_value=1000,
    max_value=3000,
    value=1500,
    step=10
)

torque = st.sidebar.number_input(
    "Torque [Nm]",
    min_value=10.0,
    max_value=80.0,
    value=50.0,
    step=0.1
)

tool_wear = st.sidebar.number_input(
    "Tool Wear [min]",
    min_value=0,
    max_value=300,
    value=100,
    step=1
)


# =========================================================
# 5. PREDICTION BUTTON
# =========================================================

predict_button = st.sidebar.button(
    "🔍 Predict Machine Failure"
)


# =========================================================
# 6. MAIN INFORMATION
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Machine Type",
        machine_type
    )

with col2:
    st.metric(
        "Rotational Speed",
        f"{rotational_speed} rpm"
    )

with col3:
    st.metric(
        "Tool Wear",
        f"{tool_wear} min"
    )


st.divider()


# =========================================================
# 7. PREDICTION
# =========================================================

if predict_button:

    # Create input dataframe
    input_data = pd.DataFrame({
        "Air temperature [K]": [air_temperature],
        "Process temperature [K]": [process_temperature],
        "Rotational speed [rpm]": [rotational_speed],
        "Torque [Nm]": [torque],
        "Tool wear [min]": [tool_wear],
        "Type_L": [1 if machine_type == "L" else 0],
        "Type_M": [1 if machine_type == "M" else 0]
    })


    # Make prediction
    prediction = model.predict(input_data)[0]

    # Get probability of failure
    failure_probability = model.predict_proba(
        input_data
    )[0][1]

    failure_percentage = failure_probability * 100


    # =====================================================
    # 8. DISPLAY RESULT
    # =====================================================

    st.subheader("Prediction Result")

    st.metric(
        "Failure Probability",
        f"{failure_percentage:.2f}%"
    )


    if prediction == 1:

        st.error(
            "⚠️ MACHINE FAILURE RISK"
        )

        st.warning(
            "The model predicts that this machine may be at risk "
            "of failure. Maintenance inspection is recommended."
        )

    else:

        st.success(
            "✅ MACHINE NORMAL"
        )

        st.info(
            "The model does not currently predict a machine failure."
        )


    # =====================================================
    # 9. SHOW INPUT DATA
    # =====================================================

    st.subheader("Machine Data Used for Prediction")

    display_data = pd.DataFrame({
        "Parameter": [
            "Machine Type",
            "Air Temperature",
            "Process Temperature",
            "Rotational Speed",
            "Torque",
            "Tool Wear"
        ],
        "Value": [
            machine_type,
            f"{air_temperature} K",
            f"{process_temperature} K",
            f"{rotational_speed} rpm",
            f"{torque} Nm",
            f"{tool_wear} min"
        ]
    })

    st.table(display_data)


# =========================================================
# 10. PROJECT INFORMATION
# =========================================================

st.divider()

st.subheader("About This Project")

st.write(
    """
    This project uses Machine Learning to predict potential
    failures in industrial machines before breakdown occurs.

    The system uses machine operating conditions such as
    temperature, rotational speed, torque and tool wear.

    A Random Forest classification model is used to estimate
    the probability of machine failure.
    """
)

st.caption(
    "AI-Based Predictive Maintenance | Random Forest Model"
)