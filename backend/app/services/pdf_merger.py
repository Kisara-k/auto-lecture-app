import fitz
import os
import re
from typing import List, Optional, BinaryIO
from fastapi import HTTPException
from ..utils.temp_utils import create_temp_file, get_temp_dir, save_temp_file

def strip_bookmarks(pdf_path: str) -> Optional[fitz.Document]:
    """Open a PDF, remove bookmarks by creating a new doc with all pages."""
    try:
        # Verify file exists and is readable
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not os.access(pdf_path, os.R_OK):
            raise PermissionError(f"Cannot read PDF file: {pdf_path}")
        
        # Check file size
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            raise ValueError(f"PDF file is empty: {pdf_path}")
        
        original = fitz.open(pdf_path)
        cleaned = fitz.open()
        cleaned.insert_pdf(original)
        original.close()
        return cleaned
    except Exception as e:
        print(f"Failed to process '{pdf_path}': {e}")
        return None

async def merge_pdfs(pdf_files: List[tuple[str, bytes]]) -> bytes:
    """
    Merge multiple PDF files into a single PDF.
    
    Args:
        pdf_files: List of tuples containing (filename, file_content)
        
    Returns:
        bytes: The merged PDF content
    """
    if not pdf_files:
        raise HTTPException(status_code=400, detail="No PDF files provided")

    # Sort files by name to maintain order
    pdf_files = sorted(pdf_files, key=lambda x: x[0])
    
    merged_doc = fitz.open()
    toc = []
    page_counter = 0

    temp_files = []
    
    try:
        for filename, file_content in pdf_files:
            # Create temporary file for processing using local temp directory
            temp_file_path = create_temp_file(suffix='.pdf', prefix=f"merge_{filename}_")
            temp_files.append(temp_file_path)
            
            try:
                # Write content to temporary file
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(file_content)
                
                # Ensure file is fully written and closed before processing
                cleaned_doc = strip_bookmarks(str(temp_file_path))
                
                if cleaned_doc is None or cleaned_doc.page_count == 0:
                    print(f"Skipping empty or invalid PDF: {filename}")
                    continue

                merged_doc.insert_pdf(cleaned_doc)

                # Remove leading zeros from the title
                bookmark_title = os.path.splitext(filename)[0]
                match = re.match(r'^(\d+)(.*)', bookmark_title)
                if match:
                    raw_number, rest = match.groups()
                    rest = rest.lstrip()

                    # Always strip leading zeros if the number has more than one digit and starts with zero
                    if len(raw_number) > 1 and raw_number.startswith("0"):
                        number_part = str(int(raw_number))
                    else:
                        number_part = raw_number

                    if not rest.startswith('.'):
                        bookmark_title = f"{number_part}. {rest}"
                    else:
                        bookmark_title = number_part + rest

                toc.append([1, bookmark_title, page_counter + 1])
                page_counter += cleaned_doc.page_count

                cleaned_doc.close()
                
            except Exception as e:
                print(f"Error processing file '{filename}': {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error processing file '{filename}': {str(e)}")

        if page_counter == 0:
            raise HTTPException(status_code=400, detail="No valid PDF content found to merge")

        merged_doc.set_toc(toc)
        
        # Save to bytes
        pdf_bytes = merged_doc.tobytes()
        merged_doc.close()
        
        # Save merged PDF to local temp directory for later use
        merged_pdf_path = save_temp_file(pdf_bytes, "merged_lectures.pdf")
        print(f"Merged PDF saved to: {merged_pdf_path}")
        
        return pdf_bytes
        
    finally:
        # Clean up temporary files
        for temp_file_path in temp_files:
            try:
                temp_file_path.unlink()
            except Exception:
                pass
