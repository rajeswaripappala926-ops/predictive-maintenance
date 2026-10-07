const form = document.getElementById("predictionForm");

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    // Get values from form
    const machineType = document.getElementById("machine_type").value;
    const airTemperature = parseFloat(
        document.getElementById("air_temperature").value
    );
    const processTemperature = parseFloat(
        document.getElementById("process_temperature").value
    );
    const rotationalSpeed = parseFloat(
        document.getElementById("rotational_speed").value
    );
    const torque = parseFloat(
        document.getElementById("torque").value
    );
    const toolWear = parseFloat(
        document.getElementById("tool_wear").value
    );


    // Show analyzing message
    const resultBox = document.getElementById("resultBox");

    resultBox.innerHTML = `
        <div class="result-icon">⏳</div>
        <h3>Analyzing Machine...</h3>
        <p>AI model is checking the sensor parameters.</p>
    `;


    try {

        // Send data to FastAPI backend
        const response = await fetch("http://127.0.0.1:8000/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                machine_type: machineType,
                air_temperature: airTemperature,
                process_temperature: processTemperature,
                rotational_speed: rotationalSpeed,
                torque: torque,
                tool_wear: toolWear
            })
        });


        // Convert response to JSON
        const result = await response.json();


        // Handle backend error
        if (!response.ok) {
            throw new Error(
                result.detail || "Prediction request failed"
            );
        }


        // Get result values
        const status = result.status;
        const probability = result.failure_probability;
        const message = result.message;


        // Update probability
        document.getElementById("probability").textContent =
            probability + "%";

        document.getElementById("progress").style.width =
            probability + "%";


        // Show result
        if (result.prediction === 1) {

            resultBox.innerHTML = `
                <div class="result-icon">⚠️</div>

                <h3>Failure Risk Detected</h3>

                <p>
                    ${message}
                </p>
            `;

        } else {

            resultBox.innerHTML = `
                <div class="result-icon">✅</div>

                <h3>Machine Normal</h3>

                <p>
                    ${message}
                </p>
            `;
        }


        console.log("Prediction:", result);

    } catch (error) {

        console.error("Error:", error);

        resultBox.innerHTML = `
            <div class="result-icon">❌</div>

            <h3>Connection Error</h3>

            <p>
                Could not connect to the FastAPI backend.
                Please make sure the backend server is running.
            </p>
        `;
    }

});