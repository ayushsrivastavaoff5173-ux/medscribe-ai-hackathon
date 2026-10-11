import os
<<<<<<< HEAD
import time
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

client = genai.Client(api_key=API_KEY) if API_KEY else None
=======
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json

load_dotenv()
>>>>>>> bec17c2 (Update FastAPI backend routes, configure Gemini 3.8 model, and fix frontend UI)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD

class NotesRequest(BaseModel):
    conversation: str


class Medication(BaseModel):
    name: str
    dose: str
    frequency: str
    duration: str


class MedicalNotes(BaseModel):
    chief_complaint: str
    history_of_present_illness: str
    symptoms: List[str]
    diagnosis: str
    icd10_code: str
    medications: List[Medication]
    allergies: List[str]
    advice: List[str]
    follow_up: str


SYSTEM_PROMPT = """You are a medical scribe assistant. Convert the doctor-patient
conversation into structured clinical notes.
Rules:
- Use ONLY information present in the conversation. Never invent details.
- The transcript may have no speaker labels; infer who is the doctor and patient.
- If something is not mentioned, write "Not mentioned" (or an empty list).
- diagnosis: only if the doctor states or clearly implies one, otherwise "Not mentioned".
- icd10_code: a suggested ICD-10 code for that diagnosis, or an empty string if no diagnosis.
- For each medication, fill dose, frequency and duration only if stated; otherwise "Not specified".
- Keep the language concise and clinical.
- The conversation may be in English, Hindi or Hinglish; write the notes in English."""


=======
# Initialize Gemini Client (automatically reads GEMINI_API_KEY from .env)
client = genai.Client()

class ConsultationRequest(BaseModel):
    conversation: str

>>>>>>> bec17c2 (Update FastAPI backend routes, configure Gemini 3.8 model, and fix frontend UI)
@app.get("/")
def root():
    return {"status": "MedScribe AI Backend is running!"}

<<<<<<< HEAD

@app.post("/generate-notes", response_model=MedicalNotes)
def generate_notes(req: NotesRequest):
    if client is None:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set in backend/.env")
    if not req.conversation.strip():
        raise HTTPException(status_code=400, detail="Conversation is empty")

    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=req.conversation,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=MedicalNotes,
                    temperature=0.2,
                ),
            )
            return response.parsed
        except Exception as e:
            last_error = e
            # Gemini busy (503) ya rate limit (429) ho to thoda ruk ke dobara try karo
            if "503" in str(e) or "429" in str(e):
                time.sleep(2 * (attempt + 1))
                continue
            break

    raise HTTPException(status_code=503, detail=f"Gemini busy/error: {last_error}")
=======
@app.post("/generate-notes")
def generate_notes(req: ConsultationRequest):
    try:
        prompt = f"""
        You are an expert medical AI scribe. Analyze the following doctor-patient consultation transcript and extract structured EMR clinical notes.
        You must return ONLY a valid JSON object with the following exact keys:
        - "chief_complaint": A concise summary of the patient's main symptoms and history.
        - "diagnosis": The medical diagnosis.
        - "icd10_code": The corresponding ICD-10 code tag (e.g., J04.0).
        - "medications": An array of objects, where each object has "name", "dose", "frequency", and "duration". If a value is unknown, use "Not specified".

        Transcript:
        {req.conversation}
        """

        model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        notes = json.loads(response.text)
        return notes

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
>>>>>>> bec17c2 (Update FastAPI backend routes, configure Gemini 3.8 model, and fix frontend UI)
