"""
PDF Test Script for Auto Lecture App

This script helps test and debug PDF processing issues.
It creates sample PDFs and tests the merge functionality.
"""

import fitz  # PyMuPDF
import tempfile
import os
from pathlib import Path

def create_sample_pdf(content: str, filename: str) -> str:
    """Create a simple PDF with text content for testing"""
    doc = fitz.open()
    page = doc.new_page()
    
    # Add text to the page
    text_rect = fitz.Rect(50, 50, 500, 700)
    page.insert_textbox(text_rect, content, fontsize=12, fontname="helv")
    
    # Save to temp directory
    temp_dir = Path("test_pdfs")
    temp_dir.mkdir(exist_ok=True)
    
    file_path = temp_dir / filename
    doc.save(str(file_path))
    doc.close()
    
    return str(file_path)

def test_pdf_merge():
    """Test PDF merging functionality"""
    print("Testing PDF merge functionality...")
    
    # Create sample PDFs
    pdf1_content = """
    Lecture 1: Introduction to Machine Learning
    
    This is the first lecture covering basic concepts of machine learning.
    We will explore supervised and unsupervised learning methods.
    
    Key topics:
    - What is Machine Learning?
    - Types of Learning
    - Common Algorithms
    - Applications
    """
    
    pdf2_content = """
    Lecture 2: Neural Networks
    
    This lecture covers neural networks and deep learning fundamentals.
    We will build our first neural network from scratch.
    
    Key topics:
    - Neurons and Layers
    - Activation Functions
    - Backpropagation
    - Training Process
    """
    
    pdf3_content = """
    Lecture 3: Data Preprocessing
    
    Learn how to clean and prepare data for machine learning models.
    Data quality is crucial for model performance.
    
    Key topics:
    - Data Cleaning
    - Feature Engineering
    - Normalization
    - Handling Missing Data
    """
    
    try:
        # Create test PDFs
        pdf1_path = create_sample_pdf(pdf1_content, "01_introduction_ml.pdf")
        pdf2_path = create_sample_pdf(pdf2_content, "02_neural_networks.pdf")
        pdf3_path = create_sample_pdf(pdf3_content, "03_data_preprocessing.pdf")
        
        print(f"Created test PDF: {pdf1_path}")
        print(f"Created test PDF: {pdf2_path}")
        print(f"Created test PDF: {pdf3_path}")
        
        # Test opening each PDF
        for pdf_path in [pdf1_path, pdf2_path, pdf3_path]:
            print(f"\nTesting PDF: {pdf_path}")
            
            # Check file properties
            file_size = os.path.getsize(pdf_path)
            print(f"   File size: {file_size} bytes")
            
            # Test opening with PyMuPDF
            try:
                doc = fitz.open(pdf_path)
                print(f"   Successfully opened with PyMuPDF")
                print(f"   Pages: {doc.page_count}")
                
                # Test reading content
                if doc.page_count > 0:
                    page = doc.load_page(0)
                    text = page.get_text()
                    print(f"   Text length: {len(text)} characters")
                    print(f"   First 100 chars: {text[:100]}...")
                
                doc.close()
            except Exception as e:
                print(f"   Failed to open: {e}")
        
        # Test merging
        print(f"\nTesting merge functionality...")
        merged_doc = fitz.open()
        toc = []
        page_counter = 0
        
        for i, pdf_path in enumerate([pdf1_path, pdf2_path, pdf3_path], 1):
            try:
                doc = fitz.open(pdf_path)
                merged_doc.insert_pdf(doc)
                
                # Add bookmark
                filename = os.path.basename(pdf_path)
                title = os.path.splitext(filename)[0]
                toc.append([1, title, page_counter + 1])
                page_counter += doc.page_count
                
                doc.close()
                print(f"   Merged {filename}")
            except Exception as e:
                print(f"   Failed to merge {pdf_path}: {e}")
        
        # Save merged PDF
        merged_doc.set_toc(toc)
        merged_path = "test_pdfs/merged_lectures.pdf"
        merged_doc.save(merged_path)
        merged_doc.close()
        
        print(f"Merged PDF saved: {merged_path}")
        print(f"   Total pages: {page_counter}")
        print(f"   Bookmarks: {len(toc)}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def test_problematic_pdf():
    """Test with various edge cases that might cause issues"""
    print("\nTesting edge cases...")
    
    try:
        # Test empty PDF
        empty_doc = fitz.open()
        empty_path = "test_pdfs/empty.pdf"
        empty_doc.save(empty_path)
        empty_doc.close()
        print(f"Created empty PDF: {empty_path}")
        
        # Test opening empty PDF
        try:
            doc = fitz.open(empty_path)
            print(f"   Pages in empty PDF: {doc.page_count}")
            doc.close()
        except Exception as e:
            print(f"   Error with empty PDF: {e}")
        
        # Test corrupted filename (with special characters)
        special_content = "PDF with special filename characters"
        special_path = create_sample_pdf(special_content, "04_special-chars_&_symbols.pdf")
        print(f"Created PDF with special characters: {special_path}")
        
        return True
        
    except Exception as e:
        print(f"Edge case test failed: {e}")
        return False

def diagnose_temp_file_issues():
    """Diagnose temporary file handling issues"""
    print("\nDiagnosing temporary file handling...")
    
    try:
        # Test tempfile creation
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
            print(f"   Created temp file: {temp_path}")
            
            # Write some content
            sample_doc = fitz.open()
            page = sample_doc.new_page()
            page.insert_text((50, 50), "Test content")
            sample_doc.save(temp_path)
            sample_doc.close()
            
        # Test opening the temp file
        print(f"   Testing temp file access...")
        if os.path.exists(temp_path):
            print(f"   Temp file exists")
            print(f"   Size: {os.path.getsize(temp_path)} bytes")
            print(f"   Readable: {os.access(temp_path, os.R_OK)}")
            
            # Test opening with PyMuPDF
            try:
                doc = fitz.open(temp_path)
                print(f"   Successfully opened temp PDF")
                print(f"   Pages: {doc.page_count}")
                doc.close()
            except Exception as e:
                print(f"   Failed to open temp PDF: {e}")
            
        else:
            print(f"   Temp file does not exist")
        
        # Clean up
        try:
            os.unlink(temp_path)
            print(f"   Cleaned up temp file")
        except Exception as e:
            print(f"   Failed to clean up temp file: {e}")
            
        return True
        
    except Exception as e:
        print(f"Temp file test failed: {e}")
        return False

def main():
    print("PDF Test Suite - Auto Lecture App")
    print("=" * 50)
    
    # Test 1: Basic PDF merge
    success1 = test_pdf_merge()
    
    # Test 2: Edge cases
    success2 = test_problematic_pdf()
    
    # Test 3: Temporary file handling
    success3 = diagnose_temp_file_issues()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"   Basic merge test: {'PASS' if success1 else 'FAIL'}")
    print(f"   Edge cases test: {'PASS' if success2 else 'FAIL'}")
    print(f"   Temp file test: {'PASS' if success3 else 'FAIL'}")
    
    if all([success1, success2, success3]):
        print("\nAll tests passed! PDF processing should work correctly.")
        print("\nTest files created in 'test_pdfs/' directory")
        print("   You can use these files to test the web interface:")
        print("   1. Start the backend: cd backend && python main.py")
        print("   2. Start the frontend: cd frontend && python serve.py")
        print("   3. Upload the test PDFs from 'test_pdfs/' folder")
    else:
        print("\nSome tests failed. Check the error messages above.")
        print("   Common issues:")
        print("   - PyMuPDF not installed: pip install PyMuPDF")
        print("   - File permissions issues")
        print("   - Temporary directory access problems")

if __name__ == "__main__":
    main()
