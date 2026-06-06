"""
test_pipeline.py
----------------
Tests for every component of TalentScout AI.
Run with: python tests/test_pipeline.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pdf_reader import extract_text_from_pdf, extract_text_from_bytes
from src.config import settings


def test_separator():
    print("\n" + "="*60)


def test_config():
    """Test 1: Verify configuration loads correctly."""
    test_separator()
    print("TEST 1: Configuration")
    
    assert settings.CHUNK_SIZE > 0, "Chunk size must be positive"
    assert settings.CHUNK_OVERLAP < settings.CHUNK_SIZE, "Overlap must be less than chunk size"
    assert settings.TOP_K_RESULTS > 0, "Must retrieve at least 1 result"
    
    if settings.is_api_key_valid:
        print("  ✅ API key is configured")
    else:
        print("  ⚠️  API key NOT configured - AI features will fail")
    
    print(f"  ✅ Chunk size: {settings.CHUNK_SIZE}")
    print(f"  ✅ Chunk overlap: {settings.CHUNK_OVERLAP}")
    print("  ✅ Config test PASSED\n")


def test_pdf_reader():
    """Test 2: Verify PDF reader works."""
    test_separator()
    print("TEST 2: PDF Reader")
    
    test_pdf = "data/sample_resumes/test_resume.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"  ⚠️  Skipping: No PDF at {test_pdf}")
        return
    
    text = extract_text_from_pdf(test_pdf)
    
    assert isinstance(text, str), "Output must be a string"
    assert len(text) > settings.MIN_RESUME_TEXT_LENGTH, "Too little text extracted"
    
    print(f"  ✅ Extracted {len(text)} characters")
    print(f"  ✅ First 100 chars: {text[:100]!r}")
    print("  ✅ PDF reader test PASSED\n")


def test_chunking():
    """Test 3: Verify text chunking works."""
    test_separator()
    print("TEST 3: Text Chunking")
    
    from src.rag_engine import chunk_text
    
    sample_text = "Python developer with 3 years experience. " * 50  # 2150 chars
    chunks = chunk_text(sample_text)
    
    assert len(chunks) > 0, "Must produce at least 1 chunk"
    assert all(hasattr(c, 'page_content') for c in chunks), "Chunks must be Document objects"
    assert all(len(c.page_content) <= settings.CHUNK_SIZE + 100 for c in chunks), "Chunks too large"
    
    print(f"  ✅ Input: {len(sample_text)} characters")
    print(f"  ✅ Output: {len(chunks)} chunks")
    print(f"  ✅ First chunk length: {len(chunks[0].page_content)} chars")
    print("  ✅ Chunking test PASSED\n")


def test_api_health():
    """Test 4: Check if FastAPI server is running."""
    test_separator()
    print("TEST 4: FastAPI Health Check")
    
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("  ✅ FastAPI server is running")
            data = response.json()
            print(f"  ✅ API Key configured: {data.get('api_key_configured')}")
        else:
            print(f"  ⚠️  Server returned status {response.status_code}")
    except requests.ConnectionError:
        print("  ⚠️  FastAPI server not running (start it with: uvicorn src.main:app --reload)")
    print()


def run_all_tests():
    """Run all tests and report results."""
    print("\n🧪 TALENTSCOUT AI - TEST SUITE")
    print("="*60)
    
    test_config()
    test_pdf_reader()
    test_chunking()
    test_api_health()
    
    print("="*60)
    print("✅ All tests completed!\n")


if __name__ == "__main__":
    run_all_tests()