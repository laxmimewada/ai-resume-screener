# 🎯 TalentScout AI — RAG-Driven Resume Screener

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-yellow.svg)](https://langchain.com)

> An intelligent resume screening tool powered by **Retrieval-Augmented Generation (RAG)**. Upload any PDF resume, ask a question, and get AI-powered insights in seconds.

---

## 📸 Demo

<!-- Add screenshots here after you run the app -->
*Upload a resume → Ask a question → Get intelligent analysis*

---

## 🧠 Architecture
┌─────────────────┐     HTTP POST      ┌──────────────────────┐
│  Streamlit UI   │ ─────────────────> │   FastAPI Backend    │
│  (app.py)       │ <───────────────── │   (src/main.py)      │
└─────────────────┘     JSON Response  └──────────┬───────────┘
│
┌──────────▼───────────┐
│    RAG Engine        │
│  (src/rag_engine.py) │
└──────────┬───────────┘
│
┌────────────────────┼────────────────────┐
│                    │                    │
┌─────────▼──────┐  ┌──────────▼──────┐  ┌────────▼────────┐
│  PDF Reader    │  │   ChromaDB      │  │  Google Gemini  │
│ (pypdf)        │  │ (Vector Store)  │  │  (LLM)          │
└────────────────┘  └─────────────────┘  └─────────────────┘

## 🔄 Data Flow

1. **User** uploads a PDF resume via Streamlit
2. **Streamlit** sends the file + question to FastAPI via HTTP POST
3. **FastAPI** validates the request and calls the RAG engine
4. **PDF Reader** extracts raw text from the PDF
5. **LangChain Splitter** breaks text into 1000-char overlapping chunks
6. **Google Embeddings** converts each chunk into a vector (list of numbers)
7. **ChromaDB** stores vectors locally for similarity search
8. **Retriever** finds the top-4 most relevant chunks for the question
9. **Google Gemini** reads the chunks + question and generates an answer
10. **FastAPI** returns the answer as JSON to Streamlit
11. **Streamlit** displays the answer beautifully

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API Key (free at [aistudio.google.com](https://aistudio.google.com/app/apikey))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-resume-screener.git
cd ai-resume-screener

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running the App

Open **two terminals** (both with venv activated):

**Terminal 1 — Backend:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

---

## 📁 Project Structure
ai-resume-screener/
├── src/
│   ├── init.py
│   ├── main.py          # FastAPI application
│   ├── rag_engine.py    # Core RAG pipeline
│   ├── pdf_reader.py    # PDF text extraction
│   ├── config.py        # Configuration settings
│   └── logger.py        # Logging setup
├── tests/
│   └── test_pipeline.py # Test suite
├── data/
│   └── sample_resumes/  # Place test PDFs here
├── logs/                # Auto-generated logs
├── app.py               # Streamlit frontend
├── requirements.txt
├── .env.example         # Template for .env
└── README.md

---

## 🔑 Environment Variables

Create a `.env` file based on `.env.example`:

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ Yes |
| `CHUNK_SIZE` | Text chunk size (default: 1000) | No |
| `CHUNK_OVERLAP` | Chunk overlap (default: 200) | No |
| `TOP_K_RESULTS` | Chunks to retrieve (default: 4) | No |

---

## 🧪 Running Tests

```bash
python tests/test_pipeline.py
```

---

## 💡 Sample Questions to Ask

- "What programming languages does this candidate know?"
- "How many years of work experience does this candidate have?"
- "Is this candidate a good fit for a backend developer role?"
- "What is the candidate's highest educational qualification?"
- "Summarize the candidate's key achievements."

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| AI/LLM | Google Gemini 1.5 Flash |
| Embeddings | Google Embedding-001 |
| Vector DB | ChromaDB |
| RAG Framework | LangChain |
| PDF Processing | PyPDF |

---

## 📈 Future Improvements (Version 2)

- [ ] Multi-resume batch analysis
- [ ] Candidate ranking/scoring system
- [ ] Export reports as PDF
- [ ] Support for DOCX resumes
- [ ] Job description matching score
- [ ] Authentication system

---

## 👤 Author

**Laxmi** — Final Year Integrated M.Tech (CSE - Computational and Data Science)
Vellore Institute of Technology

---

## 📄 License

MIT License — feel free to use this for learning!