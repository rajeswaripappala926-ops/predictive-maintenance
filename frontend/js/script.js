```javascript
// ======================================================
// PREDICTIVE MAINTENANCE AI
// FRONTEND SCRIPT
// ======================================================


// ======================================================
// API CONFIGURATION
// ======================================================

// Local FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000";


// ======================================================
// GET HTML ELEMENTS
// ======================================================

const form = document.getElementById("predictionForm");

const resultBox = document.getElementById("resultBox");

const analyzeButton = document.getElementById("analyzeButton");

const historyButton = document.getElementById("historyButton");

const closeHistoryButton =
    document.getElementById("closeHistoryButton");

const refreshHistoryButton =
    document.getElementById("refreshHistoryButton");


// ======================================================
// SHOW / HIDE HISTORY
// ======================================================

function toggleHistory() {

    const historySection =
        document.getElementById("historySection");

    if (!historySection) {
        return;
    }

    if (
        historySection.style.display === "none" ||
        historySection.style.display === ""
    ) {

        historySection.style.display = "block";

        loadPredictionHistory();

        historySection.scrollIntoView({
            behavior: "smooth"
        });

    } else {

        historySection.style.display = "none";

    }
}


// History button
if (historyButton) {

    historyButton.addEventListener(
        "click",
        toggleHistory
    );

}


// Close history button
if (closeHistoryButton) {

    closeHistoryButton.addEventListener(
        "click",
        function () {

            const historySection =
                document.getElementById("historySection");

            historySection.style.display = "none";

        }
    );

}


// Refresh history button
if (refreshHistoryButton) {

    refreshHistoryButton.addEventListener(
        "click",
        loadPredictionHistory
    );

}


// ======================================================
// SHOW LOADING STATE
// ======================================================

function showLoading() {

    resultBox.style.display = "block";

    document.getElementById(
        "resultMessage"
    ).textContent =
        "AI model is analyzing the machine sensor values...";

    document.getElementById(
        "statusBadge"
    ).textContent =
        "ANALYZING";

    document.getElementById(
        "probability"
    ).textContent =
        "Loading...";

    document.getElementById(
        "progress"
    ).style.width =
        "0%";

    document.getElementById(
        "riskLevel"
    ).textContent =
        "ANALYZING";

    document.getElementById(
        "healthScore"
    ).textContent =
        "--";

    document.getElementById(
        "databaseStatus"
    ).textContent =
        "Saving...";

    document.getElementById(
        "riskExplanation"
    ).textContent =
        "The AI model is checking the sensor values.";

    document.getElementById(
        "maintenanceRecommendation"
    ).textContent =
        "Generating maintenance recommendation...";

    document.getElementById(
        "maintenanceActions"
    ).innerHTML =
        "<li>Analyzing machine condition...</li>";

    document.getElementById(
        "systemMessage"
    ).textContent =
        "Please wait while the AI completes the analysis.";

}


// ======================================================
// DISPLAY PREDICTION RESULT
// ======================================================

function displayPredictionResult(result) {

    resultBox.style.display = "block";


    // ----------------------------------------------
    // Probability
    // ----------------------------------------------

    const probability =
        Number(result.failure_probability || 0);

    document.getElementById(
        "probability"
    ).textContent =
        probability + "%";


    // ----------------------------------------------
    // Progress bar
    // ----------------------------------------------

    const progress =
        document.getElementById("progress");

    progress.style.width =
        Math.min(Math.max(probability, 0), 100) + "%";


    // ----------------------------------------------
    // Status
    // ----------------------------------------------

    const statusBadge =
        document.getElementById("statusBadge");

    statusBadge.textContent =
        result.status || "UNKNOWN";


    // ----------------------------------------------
    // Risk level
    // ----------------------------------------------

    const riskLevel =
        result.risk_level || "LOW";

    document.getElementById(
        "riskLevel"
    ).textContent =
        riskLevel;


    // ----------------------------------------------
    // Health score
    // ----------------------------------------------

    const healthScore =
        Number(result.health_score || 0);

    document.getElementById(
        "healthScore"
    ).textContent =
        healthScore + "%";


    // ----------------------------------------------
    // Database status
    // ----------------------------------------------

    document.getElementById(
        "databaseStatus"
    ).textContent =
        result.database_status ||
        "Connected";


    // ----------------------------------------------
    // Result message
    // ----------------------------------------------

    document.getElementById(
        "resultMessage"
    ).textContent =
        result.status === "Failure Risk"
            ? "The AI detected an increased risk of machine failure."
            : "The machine is currently operating within a stable pattern.";


    // ----------------------------------------------
    // Risk explanation
    // ----------------------------------------------

    document.getElementById(
        "riskExplanation"
    ).textContent =
        result.risk_explanation ||
        "No significant risk indicators detected.";


    // ----------------------------------------------
    // Maintenance recommendation
    // ----------------------------------------------

    document.getElementById(
        "maintenanceRecommendation"
    ).textContent =
        result.maintenance_recommendation ||
        "Continue monitoring machine condition.";


    // ----------------------------------------------
    // Maintenance actions
    // ----------------------------------------------

    const actions =
        document.getElementById(
            "maintenanceActions"
        );

    actions.innerHTML = "";

    if (
        result.maintenance_actions &&
        result.maintenance_actions.length > 0
    ) {

        result.maintenance_actions.forEach(
            function (action) {

                const li =
                    document.createElement("li");

                li.textContent =
                    action;

                actions.appendChild(li);

            }
        );

    } else {

        const li =
            document.createElement("li");

        li.textContent =
            "Continue monitoring machine condition.";

        actions.appendChild(li);

    }


    // ----------------------------------------------
    // System message
    // ----------------------------------------------

    document.getElementById(
        "systemMessage"
    ).textContent =
        result.message ||
        "Machine analysis completed successfully.";


    // ----------------------------------------------
    // Risk CSS classes
    // ----------------------------------------------

    resultBox.classList.remove(
        "risk-low",
        "risk-medium",
        "risk-high"
    );


    if (riskLevel === "LOW") {

        resultBox.classList.add(
            "risk-low"
        );

    } else if (riskLevel === "MEDIUM") {

        resultBox.classList.add(
            "risk-medium"
        );

    } else if (riskLevel === "HIGH") {

        resultBox.classList.add(
            "risk-high"
        );

    }


    console.log(
        "Prediction Result:",
        result
    );

}


// ======================================================
// MACHINE PREDICTION
// ======================================================

if (form) {

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            // ------------------------------------------
            // Read input values
            // ------------------------------------------

            const machineType =
                document.getElementById(
                    "machine_type"
                ).value;

            const airTemperature =
                parseFloat(
                    document.getElementById(
                        "air_temperature"
                    ).value
                );

            const processTemperature =
                parseFloat(
                    document.getElementById(
                        "process_temperature"
                    ).value
                );

            const rotationalSpeed =
                parseFloat(
                    document.getElementById(
                        "rotational_speed"
                    ).value
                );

            const torque =
                parseFloat(
                    document.getElementById(
                        "torque"
                    ).value
                );

            const toolWear =
                parseFloat(
                    document.getElementById(
                        "tool_wear"
                    ).value
                );


            // ------------------------------------------
            // Validate values
            // ------------------------------------------

            if (
                Number.isNaN(airTemperature) ||
                Number.isNaN(processTemperature) ||
                Number.isNaN(rotationalSpeed) ||
                Number.isNaN(torque) ||
                Number.isNaN(toolWear)
            ) {

                alert(
                    "Please enter valid values for all sensor fields."
                );

                return;

            }


            // ------------------------------------------
            // Loading
            // ------------------------------------------

            showLoading();

            analyzeButton.disabled = true;

            analyzeButton.textContent =
                "⏳ Analyzing...";


            try {

                // --------------------------------------
                // Send request to FastAPI
                // --------------------------------------

                const response =
                    await fetch(
                        API_BASE_URL + "/predict",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                machine_type:
                                    machineType,

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


                // --------------------------------------
                // Read response
                // --------------------------------------

                const result =
                    await response.json();


                // --------------------------------------
                // Handle backend error
                // --------------------------------------

                if (!response.ok) {

                    throw new Error(
                        result.detail ||
                        result.error ||
                        "Prediction request failed."
                    );

                }


                // --------------------------------------
                // Display result
                // --------------------------------------

                displayPredictionResult(
                    result
                );


                // --------------------------------------
                // Update dashboard
                // --------------------------------------

                await loadDashboardStats();


                // --------------------------------------
                // Update history
                // --------------------------------------

                await loadPredictionHistory();


            } catch (error) {

                console.error(
                    "Prediction Error:",
                    error
                );


                resultBox.style.display =
                    "block";


                document.getElementById(
                    "resultMessage"
                ).textContent =
                    "Unable to complete machine analysis.";


                document.getElementById(
                    "statusBadge"
                ).textContent =
                    "ERROR";


                document.getElementById(
                    "probability"
                ).textContent =
                    "--";


                document.getElementById(
                    "riskLevel"
                ).textContent =
                    "--";


                document.getElementById(
                    "healthScore"
                ).textContent =
                    "--";


                document.getElementById(
                    "databaseStatus"
                ).textContent =
                    "Unavailable";


                document.getElementById(
                    "riskExplanation"
                ).textContent =
                    "Could not connect to the prediction service.";


                document.getElementById(
                    "maintenanceRecommendation"
                ).textContent =
                    "Please make sure the FastAPI backend is running.";


                document.getElementById(
                    "maintenanceActions"
                ).innerHTML =
                    "<li>Start the FastAPI backend and try again.</li>";


                document.getElementById(
                    "systemMessage"
                ).textContent =
                    error.message;


            } finally {

                analyzeButton.disabled =
                    false;

                analyzeButton.textContent =
                    "🤖 Analyze Machine";

            }

        }
    );

}


// ======================================================
// LOAD DASHBOARD STATISTICS
// ======================================================

async function loadDashboardStats() {

    try {

        const response =
            await fetch(
                API_BASE_URL + "/dashboard"
            );


        if (!response.ok) {

            throw new Error(
                "Dashboard request failed."
            );

        }


        const data =
            await response.json();


        document.getElementById(
            "totalPredictions"
        ).textContent =
            data.total_predictions || 0;


        document.getElementById(
            "normalMachines"
        ).textContent =
            data.normal_machines || 0;


        document.getElementById(
            "failureRisk"
        ).textContent =
            data.failure_risk || 0;


        document.getElementById(
            "averageProbability"
        ).textContent =
            (data.average_probability || 0) + "%";


    } catch (error) {

        console.error(
            "Dashboard Error:",
            error
        );

    }

}


// ======================================================
// LOAD PREDICTION HISTORY
// ======================================================

async function loadPredictionHistory() {

    try {

        const response =
            await fetch(
                API_BASE_URL + "/history"
            );


        if (!response.ok) {

            throw new Error(
                "History request failed."
            );

        }


        const history =
            await response.json();


        const historyBody =
            document.getElementById(
                "historyTableBody"
            );


        if (!historyBody) {

            return;

        }


        // ----------------------------------------------
        // No history
        // ----------------------------------------------

        if (
            !history ||
            history.length === 0
        ) {

            historyBody.innerHTML = `

                <tr>

                    <td colspan="12">
                        No prediction history available.
                    </td>

                </tr>

            `;

            return;

        }


        // ----------------------------------------------
        // Create table rows
        // ----------------------------------------------

        historyBody.innerHTML =
            history.map(
                function (item) {

                    const statusClass =
                        item.failure_prediction === "Normal"
                            ? "status-normal"
                            : "status-risk";


                    const riskClass =
                        item.risk_level === "LOW"
                            ? "risk-low"
                            : item.risk_level === "MEDIUM"
                                ? "risk-medium"
                                : "risk-high";


                    const createdDate =
                        item.created_at
                            ? new Date(
                                item.created_at
                            ).toLocaleString()
                            : "--";


                    return `

                        <tr>

                            <td>
                                ${item.id ?? "--"}
                            </td>

                            <td>
                                ${item.machine_type ?? "--"}
                            </td>

                            <td>
                                ${item.air_temperature ?? "--"} K
                            </td>

                            <td>
                                ${item.process_temperature ?? "--"} K
                            </td>

                            <td>
                                ${item.rotational_speed ?? "--"} RPM
                            </td>

                            <td>
                                ${item.torque ?? "--"} Nm
                            </td>

                            <td>
                                ${item.tool_wear ?? "--"} min
                            </td>

                            <td class="${statusClass}">
                                ${item.failure_prediction ?? "--"}
                            </td>

                            <td class="${riskClass}">
                                ${item.risk_level ?? "--"}
                            </td>

                            <td>
                                ${item.failure_probability ?? 0}%
                            </td>

                            <td>
                                ${item.health_score ?? 0}%
                            </td>

                            <td>
                                ${createdDate}
                            </td>

                        </tr>

                    `;

                }
            ).join("");


    } catch (error) {

        console.error(
            "History Error:",
            error
        );


        const historyBody =
            document.getElementById(
                "historyTableBody"
            );


        if (historyBody) {

            historyBody.innerHTML = `

                <tr>

                    <td colspan="12">
                        Could not load prediction history.
                        Please make sure the backend is running.
                    </td>

                </tr>

            `;

        }

    }

}


// ======================================================
// INITIAL PAGE LOAD
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadDashboardStats();

        loadPredictionHistory();

    }
);
```
