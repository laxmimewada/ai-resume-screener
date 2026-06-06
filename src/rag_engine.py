"""
rag_engine.py
-------------
Core AI engine using modern LangChain 0.3.x API.
No deprecated imports.
"""

import os
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHROMA_DB_PATH = "./chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 4


def validate_api_key():
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_api_key_here":
        raise ValueError(
            "GOOGLE_API_KEY is missing in your .env file.\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )


def chunk_text(text: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(text)
    print(f"[INFO] Text split into {len(chunks)} chunks")
    documents = [
        Document(page_content=chunk, metadata={"chunk_index": i})
        for i, chunk in enumerate(chunks)
    ]
    return documents


def create_vector_store(documents: list) -> Chroma:
    validate_api_key()
    print(f"[INFO] Creating embeddings for {len(documents)} chunks...")
    print("[INFO] This may take 10-30 seconds...")

    embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY,
)

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="resume",
        persist_directory=CHROMA_DB_PATH
    )
    print(f"[SUCCESS] Vector store created with {len(documents)} documents")
    return vector_store


def process_resume_and_answer(resume_text: str, question: str) -> dict:
    validate_api_key()

    # Step 1: Chunk
    print("\n[PIPELINE] Step 1: Chunking resume text...")
    documents = chunk_text(resume_text)

    # Step 2: Embed and store
    print("\n[PIPELINE] Step 2: Creating vector embeddings...")
    vector_store = create_vector_store(documents)

    # Step 3: Build retriever
    print("\n[PIPELINE] Step 3: Building retriever...")
    query_embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=GOOGLE_API_KEY,
        task_type="retrieval_query"
    )
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K_RESULTS}
    )

    # Step 4: Build LLM
    llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)
    

    # Step 5: Build prompt
    prompt_template = PromptTemplate.from_template("""
You are TalentScout AI, an expert recruitment assistant analyzing a candidate's resume.

Use ONLY the resume sections below to answer the question.
If the information is not present, say "This information is not found in the resume."
Do not make up any information.

Resume Sections:
{context}

Recruiter's Question: {question}

Answer:
""")

    # Step 6: Build LCEL chain (modern way, no deprecated RetrievalQA)
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    # Step 7: Get answer
    print(f"\n[PIPELINE] Step 5: Answering: '{question}'")
    answer = chain.invoke(question)

    # Get source docs separately for evidence
    source_docs = retriever.invoke(question)

    response = {
        "question": question,
        "answer": answer,
        "chunks_used": len(source_docs),
        "supporting_evidence": [doc.page_content[:200] for doc in source_docs]
    }

    print(f"\n[SUCCESS] Answer generated!")
    return response


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from pdf_reader import extract_text_from_pdf

    print("=== RAG Engine Test ===\n")

    test_pdf = "data/sample_resumes/test_resume.pdf"

    if not os.path.exists(test_pdf):
        print(f"[ERROR] Place a PDF resume at: {test_pdf}")
    else:
        resume_text = extract_text_from_pdf(test_pdf)
        test_question = "What programming languages does this candidate know?"
        print(f"Question: {test_question}\n")
        result = process_resume_and_answer(resume_text, test_question)
        print("\n" + "="*50)
        print("ANSWER:")
        print(result["answer"])
        print(f"\nBased on {result['chunks_used']} resume sections")