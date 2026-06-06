"""
app.py
------
Streamlit frontend for TalentScout AI.

This file creates the web UI. It:
1. Shows a file uploader for the resume PDF
2. Shows a text box for the recruiter's question
3. Calls the FastAPI backend
4. Displays the AI's response beautifully

Run with: streamlit run app.py
"""

import streamlit as st
import requests
import json
import time


# ─────────────────────────────────────────────
# PAGE CONFIGURATION (Must be first Streamlit command)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
API_BASE_URL = "http://localhost:8000"


# ─────────────────────────────────────────────
# CUSTOM CSS STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Answer box styling */
    .answer-box {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Metric card styling */
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    /* Evidence box */
    .evidence-box {
        background: #f1f3f4;
        padding: 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #555;
        margin: 0.5rem 0;
        border-left: 3px solid #764ba2;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def check_api_health() -> bool:
    """Check if the FastAPI backend is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def get_sample_questions() -> list:
    """Fetch sample questions from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/sample-questions", timeout=3)
        if response.status_code == 200:
            return response.json().get("sample_questions", [])
    except:
        pass
    # Fallback if API is not available
    return [
        "What programming languages does this candidate know?",
        "Summarize the candidate's work experience.",
        "What is the candidate's educational background?",
        "Does the candidate have leadership experience?"
    ]


def analyze_resume(pdf_file, question: str) -> dict:
    """
    Calls the FastAPI /analyze endpoint.
    
    Args:
        pdf_file: The uploaded file object from Streamlit
        question: The recruiter's question
    
    Returns:
        The API response as a dictionary
    """
    files = {"file": (pdf_file.name, pdf_file.getvalue(), "application/pdf")}
    data = {"question": question}
    
    response = requests.post(
        f"{API_BASE_URL}/analyze",
        files=files,
        data=data,
        timeout=120  # 2 minutes timeout for AI processing
    )
    
    response.raise_for_status()  # Raises exception for 4xx/5xx errors
    return response.json()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🤖 TalentScout AI")
    st.markdown("*AI-Powered Resume Screening*")
    st.divider()
    
    # API Status indicator
    st.markdown("### 🔌 API Status")
    api_healthy = check_api_health()
    if api_healthy:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Offline")
        st.warning("Start FastAPI server:\n```\nuvicorn src.main:app --reload\n```")
    
    st.divider()
    
    # Sample questions
    st.markdown("### 💡 Sample Questions")
    st.caption("Click to copy a question")
    
    sample_questions = get_sample_questions()
    for q in sample_questions[:5]:
        if st.button(q, key=f"btn_{q[:20]}", use_container_width=True):
            st.session_state["selected_question"] = q
    
    st.divider()
    st.markdown("### ℹ️ How It Works")
    st.markdown("""
    1. 📄 Upload a PDF resume
    2. ❓ Ask a question
    3. 🤖 AI analyzes the resume
    4. ✅ Get instant insights
    """)
    st.caption("Powered by Google Gemini & LangChain")


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

# Header
st.markdown('<h1 class="main-title">TalentScout AI 🎯</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Intelligent Resume Screening powered by Retrieval-Augmented Generation</p>', unsafe_allow_html=True)

# Two-column layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📄 Upload Resume")
    
    uploaded_file = st.file_uploader(
        "Drop a PDF resume here",
        type=["pdf"],
        help="Upload the candidate's resume in PDF format"
    )
    
    if uploaded_file:
        st.success(f"✅ **{uploaded_file.name}** uploaded ({uploaded_file.size:,} bytes)")
        
        # Show PDF details
        with st.expander("📊 File Details"):
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size:,} bytes ({uploaded_file.size/1024:.1f} KB)")
            st.write(f"**Type:** {uploaded_file.type}")


with col2:
    st.markdown("### ❓ Ask a Question")
    
    # Pre-fill question if a sample was clicked
    default_question = st.session_state.get("selected_question", "")
    
    question = st.text_area(
        "What would you like to know about this candidate?",
        value=default_question,
        height=120,
        placeholder="e.g., What programming languages does this candidate know?",
        help="Ask anything about the candidate's skills, experience, or qualifications"
    )
    
    # Character counter
    if question:
        st.caption(f"Question length: {len(question)} characters")


# ─── Analysis Button ────────────────────────
st.markdown("---")
center_col = st.columns([1, 2, 1])[1]

with center_col:
    analyze_button = st.button(
        "🔍 Analyze Resume",
        type="primary",
        use_container_width=True,
        disabled=(not uploaded_file or not question.strip())
    )


# ─── Run Analysis ────────────────────────────
if analyze_button:
    
    if not api_healthy:
        st.error("❌ Cannot connect to the backend. Please start the FastAPI server first.")
        st.code("uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
    
    else:
        with st.spinner("🤖 TalentScout AI is analyzing the resume..."):
            
            try:
                start_time = time.time()
                result = analyze_resume(uploaded_file, question)
                elapsed = time.time() - start_time
                
                # ── Display Results ──────────────────
                st.markdown("---")
                st.markdown("## 📊 Analysis Results")
                
                # Metrics row
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("⏱️ Analysis Time", f"{elapsed:.1f}s")
                with m2:
                    st.metric("📝 Resume Length", f"{result['analysis_metadata']['resume_length_chars']:,} chars")
                with m3:
                    st.metric("🔍 Chunks Analyzed", result['analysis_metadata']['chunks_analyzed'])
                
                # Main answer
                st.markdown("### 🎯 AI Answer")
                st.markdown(f"""
                <div class="answer-box">
                    <strong>Question:</strong> {result['question']}<br><br>
                    <strong>Answer:</strong><br>{result['answer']}
                </div>
                """, unsafe_allow_html=True)
                
                # Supporting evidence
                with st.expander("📚 Supporting Evidence (Resume Sections Used)"):
                    st.caption("These are the exact sections from the resume the AI referenced:")
                    for i, evidence in enumerate(result['analysis_metadata']['supporting_evidence']):
                        st.markdown(f"""
                        <div class="evidence-box">
                            <strong>Section {i+1}:</strong> ...{evidence}...
                        </div>
                        """, unsafe_allow_html=True)
                
                # Success toast
                st.success("✅ Analysis complete!")
                
                # Download result as JSON
                result_json = json.dumps(result, indent=2)
                st.download_button(
                    label="⬇️ Download Full Report (JSON)",
                    data=result_json,
                    file_name=f"analysis_{uploaded_file.name.replace('.pdf', '')}.json",
                    mime="application/json"
                )
                
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not reach the backend server. Is FastAPI running?")
                
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The analysis is taking too long. Try a shorter question or smaller PDF.")
                
            except requests.exceptions.HTTPError as e:
                error_detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                st.error(f"❌ API Error: {error_detail}")
                
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #999; font-size: 0.8rem;'>"
    "TalentScout AI | Built with FastAPI, LangChain, ChromaDB & Google Gemini"
    "</p>",
    unsafe_allow_html=True
)