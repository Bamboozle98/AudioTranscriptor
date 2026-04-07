let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusEl = document.getElementById("status");
const transcriptEl = document.getElementById("transcript");
const recordsEl = document.getElementById("records");

startBtn.addEventListener("click", async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      statusEl.textContent = "Uploading audio...";

      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("file", audioBlob, "recording.webm");

      try {
        const response = await fetch("/api/process", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Upload failed");
        }

        statusEl.textContent = "Processed.";
        transcriptEl.textContent = data.transcript || "";
        recordsEl.textContent = JSON.stringify(data.records || [], null, 2);
      } catch (err) {
        statusEl.textContent = `Error: ${err.message}`;
      }
    };

    mediaRecorder.start();
    statusEl.textContent = "Recording...";
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (err) {
    statusEl.textContent = `Mic error: ${err.message}`;
  }
});

stopBtn.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    statusEl.textContent = "Stopping...";
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
});