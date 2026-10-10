const API_URL = "http://127.0.0.1:8001/generate-notes";
const SPEECH_LANG = "en-IN"; // Hindi ke liye "hi-IN"

const recordBtn = document.getElementById('recordBtn');
const sampleBtn = document.getElementById('sampleBtn');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const transcriptText = document.getElementById('transcriptText');
const complaintsOutput = document.getElementById('complaintsOutput');
const diagnosisOutput = document.getElementById('diagnosisOutput');
const medicationsOutput = document.getElementById('medicationsOutput');
const exportPdfBtn = document.getElementById('exportPdfBtn');
const loadingSpinner = document.getElementById('loadingSpinner');

let isRecording = false;
let recognition = null;
let finalTranscript = "";

function setStatus(kind, message) {
    statusIndicator.className = "status-box " + kind;
    statusText.textContent = message;
}

// ---------- Live speech-to-text (browser Web Speech API) ----------
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function setupRecognition() {
    recognition = new SpeechRecognition();
    recognition.lang = SPEECH_LANG;
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const text = event.results[i][0].transcript;
            if (event.results[i].isFinal) finalTranscript += text + " ";
            else interim += text;
        }
        transcriptText.className = "";
        transcriptText.textContent = (finalTranscript + interim).trim() || "Listening...";
    };

    recognition.onerror = (e) => {
        if (e.error !== "no-speech") setStatus("idle", "Mic error: " + e.error);
    };

    // Chrome kabhi khud band kar deta hai; recording chal rahi ho to restart
    recognition.onend = () => {
        if (isRecording) recognition.start();
    };
}

recordBtn.addEventListener('click', () => {
    if (!SpeechRecognition) {
        setStatus("idle", "Live mic is not supported in this browser. Use Chrome/Edge or the sample button.");
        return;
    }
    if (!recognition) setupRecognition();

    isRecording = !isRecording;
    if (isRecording) {
        finalTranscript = "";
        recordBtn.innerHTML = '<span class="icon">⏹️</span> Stop Recording';
        recordBtn.classList.add('recording');
        setStatus("recording", "Recording consultation live...");
        transcriptText.className = "";
        transcriptText.textContent = "Listening to doctor and patient conversation...";
        recognition.start();
    } else {
        recordBtn.innerHTML = '<span class="icon">🎙️</span> Start Recording';
        recordBtn.classList.remove('recording');
        recognition.stop();
        // thoda ruko taaki last result aa jaye
        setTimeout(() => generateNotes(finalTranscript.trim()), 600);
    }
});

// ---------- Sample consultation (demo fallback) ----------
sampleBtn.addEventListener('click', () => {
    const sample =
`Doctor: Good morning Mr. Sharma, what brings you in today?
Patient: Good morning doctor. I have had a continuous dry cough and mild fever for the past three days, along with body fatigue.
Doctor: Let's check your vitals. Your temperature is 100.2°F. Lungs sound clear, but your upper respiratory tract is inflamed. I am prescribing Paracetamol for the fever and Azithromycin for the infection. Drink plenty of warm water and rest for 3 days.`;

    transcriptText.className = "";
    transcriptText.textContent = sample;
    setStatus("success", "Sample consultation loaded successfully.");
    generateNotes(sample);
});

// ---------- Backend call ----------
async function generateNotes(conversation) {
    if (!conversation) {
        setStatus("idle", "No speech captured. Try again or use the sample button.");
        return;
    }

    loadingSpinner.classList.remove('hidden');
    setStatus("idle", "Generating clinical notes with AI...");

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ conversation }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(typeof err.detail === "string" ? err.detail : "Server error " + res.status);
        }

        const notes = await res.json();
        renderNotes(notes);
        exportPdfBtn.removeAttribute('disabled');
        setStatus("success", "Clinical EMR notes successfully generated!");
    } catch (e) {
        setStatus("idle", "Failed: " + e.message + " (is the backend running?)");
    } finally {
        loadingSpinner.classList.add('hidden');
    }
}

// ---------- Render (textContent use kiya hai, AI output safe rehta hai) ----------
function renderNotes(n) {
    complaintsOutput.textContent = n.chief_complaint;

    diagnosisOutput.textContent = n.diagnosis;
    if (n.icd10_code) {
        const tag = document.createElement("span");
        tag.className = "icd-tag";
        tag.textContent = "ICD-10: " + n.icd10_code;
        diagnosisOutput.append(" ", tag);
    }

    medicationsOutput.innerHTML = "";
    if (!n.medications.length) {
        const li = document.createElement("li");
        li.textContent = "No medications mentioned";
        medicationsOutput.appendChild(li);
    }

    const isSpecified = (v) => v && v !== "Not specified";

    n.medications.forEach((m) => {
        const li = document.createElement("li");
        const strong = document.createElement("strong");
        strong.textContent = m.name + (isSpecified(m.dose) ? " " + m.dose : "");
        li.appendChild(strong);

        const details = [m.frequency, m.duration].filter(isSpecified);
        li.append(details.length ? " — " + details.join(", ") : " — dosage to be confirmed by doctor");
        medicationsOutput.appendChild(li);
    });
}

// ---------- Export PDF (abhi mock) ----------
exportPdfBtn.addEventListener('click', () => {
    alert("Success! Compiling clinical notes into formal PDF prescription...");
});