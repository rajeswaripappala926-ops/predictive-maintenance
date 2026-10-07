// ================================
// PREDICTIVE MAINTENANCE AI
// FRONTEND SCRIPT
// ================================


// ================================
// FORM ELEMENT
// ================================

const form = document.getElementById("predictionForm");


// ================================
// RISK LEVEL
// ================================

function getRiskLevel(probability) {

    if (probability < 30) {

        return {
            level: "LOW RISK",
            icon: "🟢",
            message: "Machine is healthy. Continue normal monitoring.",
            className: "risk-low"
        };

    } else if (probability < 70) {

        return {
            level: "MEDIUM RISK",
            icon: "🟡",
            message: "Monitor the machine closely. Maintenance may be required.",
            className: "risk-medium"
        };

    } else {

        return {
            level: "HIGH RISK",
            icon: "🔴",
            message: "Maintenance inspection is strongly recommended.",
            className: "risk-high"
        };

    }
}


// ================================
// MACHINE PREDICTION
// ================================

form.addEventListener("submit", async function (event) {

    event.preventDefault();


    // Get input values

    const machineType =
        document.getElementById("machine_type").value;

    const airTemperature =
        parseFloat(
            document.getElementById("air_temperature").value
        );

    const processTemperature =
        parseFloat(
            document.getElementById("process_temperature").value
        );

    const rotationalSpeed =
        parseFloat(
            document.getElementById("rotational_speed").value
        );

    const torque =
        parseFloat(
            document.getElementById("torque").value
        );

    const toolWear =
        parseFloat(
            document.getElementById("tool_wear").value
        );


    const resultBox =
        document.getElementById("resultBox");


    // Loading message

    resultBox.innerHTML = `
        <div class="result-icon">⏳</div>

        <h3>Analyzing Machine...</h3>

        <p>
            AI model is checking the sensor parameters.
        </p>
    `;


    try {

        // Send data to FastAPI

        const response = await fetch(
            "https://predictive-maintenance-ujcz.onrender.com/predict",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    machine_type: machineType,

                    air_temperature:
                        airTemperature,

                    process_temperature:
                        processTemperature,

                    rotational_speed:
                        rotationalSpeed,

                    torque:
                        torque,

                    tool_wear:
                        toolWear
                })
            }
        );


        const result = await response.json();


        // Backend error

        if (!response.ok) {

            throw new Error(
                result.detail ||
                result.error ||
                "Prediction request failed"
            );

        }


        // Prediction values

        const probability =
            result.failure_probability;

        const message =
            result.message;


        // Calculate risk level

        const risk =
            getRiskLevel(probability);


        // Show probability

        document.getElementById(
            "probability"
        ).textContent =
            probability + "%";


        // Update progress bar

        document.getElementById(
            "progress"
        ).style.width =
            probability + "%";


        // Remove previous risk classes

        resultBox.classList.remove(
            "risk-low",
            "risk-medium",
            "risk-high"
        );


        // Add current risk class

        resultBox.classList.add(
            risk.className
        );


        // Show result

        resultBox.innerHTML = `

            <div class="result-icon">
                ${risk.icon}
            </div>

            <h3>
                ${risk.level}
            </h3>

            <p>
                ${message}
            </p>

            <p>
                Failure Probability:
                <strong>${probability}%</strong>
            </p>

        `;


        console.log(
            "Prediction:",
            result
        );


        // Refresh dashboard automatically

        loadDashboardStats();


        // Refresh prediction history automatically

        loadPredictionHistory();


    } catch (error) {

        console.error(
            "Prediction Error:",
            error
        );


        resultBox.innerHTML = `

            <div class="result-icon">
                ❌
            </div>

            <h3>
                Connection Error
            </h3>

            <p>
                Could not connect to the FastAPI backend.
                Please make sure the backend server is running.
            </p>

        `;

    }

});


// ================================
// LOAD DASHBOARD STATISTICS
// ================================

async function loadDashboardStats() {

    try {

        const response = await fetch(
            "https://predictive-maintenance-ujcz.onrender.com/dashboard"
        );


        const data =
            await response.json();


        document.getElementById(
            "totalPredictions"
        ).textContent =
            data.total_predictions;


        document.getElementById(
            "normalMachines"
        ).textContent =
            data.normal_machines;


        document.getElementById(
            "failureRisk"
        ).textContent =
            data.failure_risk;


        document.getElementById(
            "averageProbability"
        ).textContent =
            data.average_probability + "%";


    } catch (error) {

        console.error(
            "Dashboard data could not be loaded:",
            error
        );

    }

}


// ================================
// LOAD PREDICTION HISTORY
// ================================

async function loadPredictionHistory() {

    try {

        const response = await fetch(
            "https://predictive-maintenance-ujcz.onrender.com/history"
        );


        const history =
            await response.json();


        const historyBody =
            document.getElementById(
                "historyBody"
            );


        // No history

        if (history.length === 0) {

            historyBody.innerHTML = `

                <tr>

                    <td colspan="10">
                        No predictions available yet.
                    </td>

                </tr>

            `;

            return;

        }


        // Create table rows

        historyBody.innerHTML =
            history.map(item => {


                const statusClass =
                    item.failure_prediction === "Normal"
                        ? "status-normal"
                        : "status-risk";


                return `

                    <tr>

                        <td>
                            ${item.id}
                        </td>

                        <td>
                            ${item.machine_type}
                        </td>

                        <td>
                            ${item.air_temperature} K
                        </td>

                        <td>
                            ${item.process_temperature} K
                        </td>

                        <td>
                            ${item.rotational_speed} RPM
                        </td>

                        <td>
                            ${item.torque} Nm
                        </td>

                        <td>
                            ${item.tool_wear} min
                        </td>

                        <td class="${statusClass}">
                            ${item.failure_prediction}
                        </td>

                        <td class="risk-value">
                            ${item.failure_probability}%
                        </td>

                        <td>
                            ${new Date(
                                item.created_at
                            ).toLocaleString()}
                        </td>

                    </tr>

                `;

            }).join("");


    } catch (error) {

        console.error(
            "History could not be loaded:",
            error
        );

    }

}


// ================================
// INITIAL DASHBOARD LOAD
// ================================

loadDashboardStats();

loadPredictionHistory();

function toggleHistory() {
    const historySection = document.querySelector(".history-section");

    if (historySection.style.display === "none") {
        historySection.style.display = "block";
    } else {
        historySection.style.display = "none";
    }
}
