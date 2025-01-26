document.getElementById("download-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const videoUrl = document.getElementById("video-url").value;
    const messageDiv = document.getElementById("message");
    
    // Show loading message
    messageDiv.textContent = "Starting download... Please wait.";
    messageDiv.style.color = "blue";

    try {
        const response = await fetch("/download-video", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ video_url: videoUrl }),
        });

        const data = await response.json();

        if (response.ok) {
            messageDiv.textContent = `${data.message}. Location: ${data.folder}`;
            messageDiv.style.color = "green";
        } else {
            messageDiv.textContent = `Error: ${data.error}`;
            messageDiv.style.color = "red";
        }
    } catch (error) {
        console.error("Error:", error);
        messageDiv.textContent = `Error: ${error.message}`;
        messageDiv.style.color = "red";
    }
}); 