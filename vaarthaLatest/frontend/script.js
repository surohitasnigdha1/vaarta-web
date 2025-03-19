document.getElementById("analyze-button").addEventListener("click", async () => {
    const text = document.getElementById("text-input").value;

    // Check if the input is empty
    if (!text) {
        alert("Please enter some text to analyze.");
        return;
    }

    // Disable the button to prevent multiple clicks
    const analyzeButton = document.getElementById("analyze-button");
    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";

    try {
        // Send a POST request to the backend
        const response = await fetch("http://localhost:8000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text }),
        });

        // Check if the response is OK
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Parse the JSON response
        const data = await response.json();
        console.log("Backend Response:", data);  // Log the backend response

        // Extract data from the response
        const label = data.label || "No label available";
        const confidence = data.confidence ? (data.confidence * 100).toFixed(2) : "N/A";
        const sources = data.sources || [];

        console.log("Extracted Sources:", sources);  // Log the extracted sources

        // Display the result in the HTML
        let resultHTML = `
            <strong>Label:</strong> ${label}<br>
            <strong>Confidence:</strong> ${confidence}%<br>
        `;

        // Add all sources if available
        if (sources.length > 0) {
            resultHTML += `<strong>Sources:</strong><br>`;
            sources.forEach((source, index) => {
                resultHTML += `
                    ${index + 1}. <a href="${source.url}" target="_blank">${source.publisher}</a><br>
                `;
            });
        } else {
            resultHTML += `<strong>Sources:</strong> No sources available<br>`;
        }

        document.getElementById("result").innerHTML = resultHTML;

        // Change the background color based on confidence
        const confidenceValue = parseFloat(confidence);
        if (!isNaN(confidenceValue)) {
            if (confidenceValue >= 70) {
                document.body.style.backgroundColor = "#d4edda"; // Green
            } else if (confidenceValue >= 40) {
                document.body.style.backgroundColor = "#fff3cd"; // Yellow
            } else {
                document.body.style.backgroundColor = "#f8d7da"; // Red
            }
        }
    } catch (error) {
        console.error("Error analyzing text:", error);
        document.getElementById("result").innerHTML = "An error occurred. Please try again.";
    } finally {
        // Re-enable the button
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze";
    }
});