"""
pdf_reader.py
-------------
This module handles reading text from PDF files.
It uses the pypdf library to extract raw text from each page.
"""

import pypdf
import os


def extract_text_from_pdf(file_path: str) -> str:
    """
    Reads a PDF file from the given path and returns all text as a string.
    
    Args:
        file_path: The full path to the PDF file.
    
    Returns:
        A single string containing all text from the PDF.
    """
    
    # Check if the file actually exists before trying to read it
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at path: {file_path}")
    
    # Check that the file is actually a PDF
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"File must be a PDF. Got: {file_path}")
    
    extracted_text = ""
    
    # Open the PDF file in read-binary mode
    with open(file_path, 'rb') as pdf_file:
        
        # Create a PDF reader object
        reader = pypdf.PdfReader(pdf_file)
        
        # Get the total number of pages
        total_pages = len(reader.pages)
        print(f"[INFO] PDF has {total_pages} page(s). Starting text extraction...")
        
        # Loop through every page and extract text
        for page_number in range(total_pages):
            page = reader.pages[page_number]
            page_text = page.extract_text()
            
            # Some pages might be blank or image-only (returns None)
            if page_text:
                extracted_text += page_text + "\n"
                print(f"[INFO] Page {page_number + 1} extracted: {len(page_text)} characters")
            else:
                print(f"[WARNING] Page {page_number + 1} had no extractable text (might be an image).")
    
    print(f"[SUCCESS] Total text extracted: {len(extracted_text)} characters")
    return extracted_text


def extract_text_from_bytes(file_bytes: bytes) -> str:
    """
    Reads a PDF from raw bytes (used when receiving file uploads via FastAPI).
    
    Args:
        file_bytes: The PDF file content as bytes.
    
    Returns:
        A single string containing all text from the PDF.
    """
    import io
    
    extracted_text = ""
    
    # Wrap the bytes in a file-like object so pypdf can read it
    pdf_file = io.BytesIO(file_bytes)
    
    reader = pypdf.PdfReader(pdf_file)
    total_pages = len(reader.pages)
    print(f"[INFO] PDF (from bytes) has {total_pages} page(s).")
    
    for page_number in range(total_pages):
        page = reader.pages[page_number]
        page_text = page.extract_text()
        if page_text:
            extracted_text += page_text + "\n"
    
    return extracted_text


# -------------------------------------------------------------------
# QUICK TEST: Run this file directly to verify it works
# python src/pdf_reader.py
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("=== PDF Reader Test ===")
    
    # We'll create a dummy test with a real PDF
    test_path = "data/sample_resumes/test_resume.pdf"
    
    if os.path.exists(test_path):
        text = extract_text_from_pdf(test_path)
        print("\n--- First 500 characters of extracted text ---")
        print(text[:500])
    else:
        print(f"[NOTE] No test PDF found at {test_path}")
        print("Place any PDF resume there and run again.")
        print("For now, the module loaded successfully!")