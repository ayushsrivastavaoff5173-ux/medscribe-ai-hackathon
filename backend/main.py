import os
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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NotesRequest(BaseModel):
    conversation: str


class MedicalNotes(BaseModel):
    chief_complaint: str
    history_of_present_illness: str
    symptoms: List[str]
    medications_mentioned: List[str]
    allergies: List[str]
    assessment: str
    plan: List[str]
    follow_up: str


SYSTEM_PROMPT = """You are a medical scribe assistant. Convert the doctor-patient
conversation into structured clinical notes.
Rules:
- Use ONLY information present in the conversation. Never invent details.
- If something is not mentioned, write "Not mentioned" (or an empty list).
- Keep the language concise and clinical.
- The conversation may be in English, Hindi or Hinglish; write the notes in English."""


@app.get("/")
def root():
    return {"status": "MedScribe AI Backend is running!"}


@app.post("/generate-notes", response_model=MedicalNotes)
def generate_notes(req: NotesRequest):
    if client is None:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set in backend/.env")
    if not req.conversation.strip():
        raise HTTPException(status_code=400, detail="Conversation is empty")

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
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")