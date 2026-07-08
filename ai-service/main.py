import uvicorn
import os
import io
import json
import tempfile
import re
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from pydub import AudioSegment
from google import genai
from google.genai import types

load_dotenv()

AI_SERVICE_PORT = int(os.getenv("AI_SERVICE_PORT", 8000))

# Initialize the Gemini API client lazily
_client = None

def get_gemini_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please configure it in your Render/Railway settings.")
        _client = genai.Client(api_key=api_key)
    return _client

app = FastAPI(title="AI Interviewer Microservice (Gemini Powered)", version="2.0")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionResquest(BaseModel):
    role: str = "MERN Stack Developer"
    level: str = "Junior"
    count: int = 5
    interview_type: str = "coding-mix"

class QuestionResponse(BaseModel):
    questions: list[str]
    model_used: str

class EvaluationRequest(BaseModel):
    question: str
    question_type: str
    role: str
    level: str
    user_answer: Optional[str] = None
    user_code: Optional[str] = None

class EvaluationResponse(BaseModel):
    technicalScore: int
    confidenceScore: int
    aiFeedback: str
    idealAnswer: str

@app.get("/")
async def root():
    return {"message": "Hello from AI Interviewer Microservice (Gemini-Powered)!", "model": "gemini-2.0-flash"}

@app.post("/generate-questions", response_model=QuestionResponse)
async def generate_questions(request: QuestionResquest):
    try:
        if request.interview_type == "coding-mix":
            coding_count = int(request.count * 0.2)
            oral_oral = int(request.count) - int(coding_count)

            instruction = (
                f"The first {coding_count} questions MUST be coding challenges requiring function implementation. "
                f"The remaining {oral_oral} questions MUST be conceptual oral questions."
            )
        else:
            instruction = "All questions MUST be conceptual oral questions. Do NOT generate any coding or implementation challenges."

        system_prompt = (
            "You are a professional technical interviewer. "
            "Task: Generate interview questions. No conversational text or numbering. "
            f"Crucial: {instruction} "
            "Output exactly one question per line."
        )

        user_prompt = (
            f"Generate exactly {request.count} unique interview questions for a {request.level} level {request.role}."
        )
        
        response = get_gemini_client().models.generate_content(
            model="gemini-2.0-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.6,
            )
        )

        raw_text = response.text.strip()
        # Clean up any potential <think> blocks or numbering/markdown formatting
        raw_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
        
        questions = []
        for line in raw_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Remove leading numbers/bullet styles, e.g. "1. ", "2) ", "- "
            clean_line = re.sub(r'^\d+[\.\)\s-]+\s*', '', line).strip()
            if clean_line:
                questions.append(clean_line)
                
        return QuestionResponse(questions=questions[:request.count], model_used="gemini-2.0-flash")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        audio_in_memory = io.BytesIO(audio_bytes)
        audio_segment = AudioSegment.from_file(audio_in_memory)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            temp_audio_path = tmp.name
            audio_segment.export(temp_audio_path, format="mp3")
            
        try:
            with open(temp_audio_path, "rb") as f:
                mp3_bytes = f.read()
                
            response = get_gemini_client().models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    "Transcribe the following audio clip exactly as spoken. Output ONLY the raw transcription text without any commentary, labels, or formatting.",
                    types.Part.from_bytes(
                        data=mp3_bytes,
                        mime_type="audio/mp3"
                    )
                ]
            )
            transcription = response.text.strip()
        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                
        return {"transcription": transcription}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    try:
        if request.question_type == "oral":
            assessment_instruction = (
                "This is a conceptual oral question. Focus purely on the candidate's Verbal Answer. "
                "Ignore any code. "
                "CRITICAL: If the Verbal Answer is empty, nonsense (e.g. 'blah blah', 'testing', 'hello'), or completely irrelevant to the question, you MUST return technicalScore: 0 and confidenceScore: 0."
            )
        else:
            assessment_instruction = (
                "This is a coding challenge question. Evaluate the Code Answer logic and efficiency. "
                "Use the Verbal Answer only for insight into their thought process. "
                "CRITICAL: If the Code Answer is empty, undefined, or random characters/comments, you MUST return technicalScore: 0 and confidenceScore: 0."
            )
        
        system_prompt = (
            "You are a strict technical interviewer. Evaluate the candidate's answer based on the role and level.\n"
            "Scale: 0-100.\n"
            "Rule 1: If the answer is completely missing, gibberish (e.g. 'blah blah', 'testing', 'hello'), or irrelevant to the question as per the critical rules, you MUST return technicalScore: 0 and confidenceScore: 0.\n"
            "Rule 2: Otherwise, rate it based on accuracy and completeness (e.g. 70-100 for good answers, lower for partial answers).\n"
            f"Context: {assessment_instruction}\n\n"
            "You MUST output your final scores and feedback matching the requested schema."
        )
        
        user_prompt = (
            f"Role: {request.role}\n"
            f"Question: {request.question}\n"
            f"Level: {request.level}\n"
            f"Verbal Answer: {request.user_answer or 'No verbal answer provided'}\n"
            f"Code Answer: {request.user_code or 'No code provided'}\n"
        )
        
        response = get_gemini_client().models.generate_content(
            model="gemini-2.0-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=EvaluationResponse
            )
        )
        
        evaluation_data = json.loads(response.text)
        return EvaluationResponse(**evaluation_data)

    except Exception as e:
        print(f"Failed to generate evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=AI_SERVICE_PORT)