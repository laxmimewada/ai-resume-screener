"""
main.py
-------
The FastAPI web server for TalentScout AI.

This file defines API endpoints that the Streamlit frontend will call.

Endpoints:
- GET  /         → Health check (is the server running?)
- POST /analyze  → Upload a resume PDF + question → get AI analysis
"""

import os
import tempfile
import traceback

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import our custom modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_reader import extract_text_from_bytes
from rag_engine import process_resume_and_answer


# ─────────────────────────────────────────────
# APP INITIALIZATION
# ─────────────────────────────────────────────
app = FastAPI(
    title="TalentScout AI",
    description="An intelligent resume screening API powered by RAG and Google Gemini",
    version="1.0.0",
    docs_url="/docs",     # Swagger UI available at http://localhost:8000/docs
    redoc_url="/redoc"    # Alternative docs at http://localhost:8000/redoc
)

# Allow the Streamlit frontend (running on a different port) to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # In production, replace * with your actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# ENDPOINT 1: Health Check
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint.
    If you can access this, the server is running.
    """
    return {
        "status": "online",
        "message": "TalentScout AI is running!",
        "version": "1.0.0",
        "docs": "Visit /docs to test the API"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    api_key_set = bool(os.getenv("GOOGLE_API_KEY")) and os.getenv("GOOGLE_API_KEY") != "your_api_key_here"
    return {
        "status": "healthy",
        "api_key_configured": api_key_set,
    }


# ─────────────────────────────────────────────
# ENDPOINT 2: Resume Analysis (Main Feature)
# ─────────────────────────────────────────────
@app.post("/analyze", tags=["Resume Analysis"])
async def analyze_resume(
    file: UploadFile = File(..., description="Upload a PDF resume"),
    question: str = Form(..., description="Your question about the candidate")
):
    """
    Analyzes a resume PDF and answers a recruiter's question.
    
    - **file**: The candidate's resume in PDF format
    - **question**: What you want to know (e.g., "Does the candidate know Python?")
    
    Returns a JSON with the AI's analysis.
    """
    
    # ── Validation ──────────────────────────────
    
    # Check that a file was actually sent
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    # Check that it's a PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are supported. You uploaded: {file.filename}"
        )
    
    # Check that a question was asked
    if not question or len(question.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Please provide a meaningful question (at least 3 characters)."
        )
    
    # ── Processing ──────────────────────────────
    
    try:
        print(f"\n[API] New request received")
        print(f"[API] File: {file.filename}")
        print(f"[API] Question: {question}")
        
        # Read the uploaded file into memory as bytes
        file_bytes = await file.read()
        
        # Check file isn't empty
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        print(f"[API] File size: {len(file_bytes)} bytes")
        
        # Step 1: Extract text from PDF bytes
        print("[API] Extracting text from PDF...")
        resume_text = extract_text_from_bytes(file_bytes)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=422,
                detail="Could not extract enough text from the PDF. It might be image-only or corrupted."
            )
        
        print(f"[API] Extracted {len(resume_text)} characters from resume")
        
        # Step 2: Run the RAG pipeline
        print("[API] Running RAG analysis...")
        result = process_resume_and_answer(resume_text, question.strip())
        
        # Step 3: Return the response
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": file.filename,
                "question": result["question"],
                "answer": result["answer"],
                "analysis_metadata": {
                    "resume_length_chars": len(resume_text),
                    "chunks_analyzed": result["chunks_used"],
                    "supporting_evidence": result["supporting_evidence"]
                }
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is (they already have proper error messages)
        raise
    
    except ValueError as e:
        # API key issues and similar config errors
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"[ERROR] Unexpected error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


# ─────────────────────────────────────────────
# ENDPOINT 3: Get Supported Questions (Bonus)
# ─────────────────────────────────────────────
@app.get("/sample-questions", tags=["Utilities"])
async def get_sample_questions():
    """Returns a list of example questions recruiters can ask."""
    return {
        "sample_questions": [
            "What programming languages does this candidate know?",
            "How many years of experience does this candidate have?",
            "What is the candidate's highest educational qualification?",
            "Has the candidate worked on any machine learning projects?",
            "What databases has this candidate worked with?",
            "Does this candidate have leadership experience?",
            "What cloud platforms has this candidate used?",
            "Is this candidate a good fit for a backend developer role?",
            "Summarize the candidate's work experience.",
            "What soft skills does this candidate demonstrate?"
        ]
    }