from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
import os
from dotenv import load_dotenv

from ..services.pdf_merger import merge_pdfs
from ..services.content_extractor import extract_content_from_pdf
from ..services.openai_service import OpenAIService
from ..models import (
    MergeResponse, ExtractionResponse, ProcessingResponse, 
    ConfigUpdate, StatusResponse
)
from ..config import config
from ..utils.temp_utils import create_temp_file, get_temp_file_path, list_temp_files

# Load environment variables
load_dotenv()

router = APIRouter()

def get_openai_service():
    """Dependency to get OpenAI service instance"""
    openai_key = os.getenv('OPENAI_KEY')
    if not openai_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return OpenAIService(openai_key)

@router.post("/merge-pdfs", response_model=MergeResponse)
async def merge_pdf_files(files: List[UploadFile] = File(...)):
    """
    Merge multiple PDF files into a single PDF with bookmarks.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate file types
    pdf_files = []
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        content = await file.read()
        pdf_files.append((file.filename, content))
    
    try:
        merged_pdf_bytes = await merge_pdfs(pdf_files)
        
        # Count pages and bookmarks (simplified estimation)
        import fitz
        
        temp_file_path = create_temp_file(suffix='.pdf', content=merged_pdf_bytes)
        try:
            doc = fitz.open(str(temp_file_path))
            page_count = doc.page_count
            bookmark_count = len(doc.get_toc())
            doc.close()
        finally:
            # Clean up temporary file
            try:
                temp_file_path.unlink()
            except Exception:
                pass
        
        # In a real application, you might want to save this to storage
        # For now, we'll just return the response
        
        return MergeResponse(
            message="PDFs merged successfully",
            page_count=page_count,
            bookmark_count=bookmark_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging PDFs: {str(e)}")

@router.post("/extract-content", response_model=ExtractionResponse)
async def extract_pdf_content(file: UploadFile = File(...)):
    """
    Extract content from a merged PDF file and structure it by lectures.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        pdf_content = await file.read()
        lectures = await extract_content_from_pdf(pdf_content)
        
        return ExtractionResponse(
            message="Content extracted successfully",
            lecture_count=len(lectures),
            lectures=lectures
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")

@router.post("/extract-content-from-merged", response_model=ExtractionResponse)
async def extract_content_from_merged_pdf():
    """
    Extract content from the merged PDF file stored in temp directory.
    """
    try:
        # Look for merged PDF in temp directory
        merged_pdf_path = get_temp_file_path("merged_lectures.pdf")
        
        if not merged_pdf_path.exists():
            raise HTTPException(status_code=404, detail="No merged PDF found. Please merge PDFs first.")
        
        # Read the merged PDF
        with open(merged_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        lectures = await extract_content_from_pdf(pdf_content)
        
        return ExtractionResponse(
            message="Content extracted successfully from merged PDF",
            lecture_count=len(lectures),
            lectures=lectures
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting content from merged PDF: {str(e)}")

@router.post("/process-lectures", response_model=ProcessingResponse)
async def process_lectures_with_ai(
    lectures_json: str = Form(...),
    max_concurrent: int = Form(3, description="Maximum concurrent API calls"),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Process lectures using OpenAI API to generate study materials.
    """
    try:
        import json
        lectures = json.loads(lectures_json)
        
        if not isinstance(lectures, list):
            raise HTTPException(status_code=400, detail="Lectures must be a list")
        
        # Validate lecture structure
        for lecture in lectures:
            if not all(key in lecture for key in ['index', 'title', 'content']):
                raise HTTPException(status_code=400, detail="Each lecture must have 'index', 'title', and 'content'")
        
        results = await openai_service.process_multiple_lectures(lectures, max_concurrent)
        
        return ProcessingResponse(
            message="Lectures processed successfully",
            total_cost=openai_service.total_cost,
            processed_count=len(results),
            results=results
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for lectures")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing lectures: {str(e)}")

@router.post("/process-complete-pipeline")
async def process_complete_pipeline(
    files: List[UploadFile] = File(...),
    max_concurrent: int = Form(3, description="Maximum concurrent API calls"),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Complete pipeline: merge PDFs → extract content → process with AI
    """
    try:
        # Step 1: Merge PDFs
        pdf_files = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            content = await file.read()
            pdf_files.append((file.filename, content))
        
        merged_pdf_bytes = await merge_pdfs(pdf_files)
        
        # Step 2: Extract content
        lectures = await extract_content_from_pdf(merged_pdf_bytes)
        
        # Step 3: Process with AI
        results = await openai_service.process_multiple_lectures(lectures, max_concurrent)
        
        return {
            "message": "Complete pipeline executed successfully",
            "total_cost": openai_service.total_cost,
            "processed_count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current configuration and status"""
    return StatusResponse(
        status="active",
        config={
            "START": config.START,
            "NUM_LECS": config.NUM_LECS,
            "MODEL": config.MODEL,
            "GET_TRANSCRIPTS": config.GET_TRANSCRIPTS,
            "GET_KEY_POINTS": config.GET_KEY_POINTS,
            "GET_Q_AND_A": config.GET_Q_AND_A,
            "TRY_REUSE_NOTES": config.TRY_REUSE_NOTES,
            "IS_BOOK": config.IS_BOOK
        }
    )

@router.post("/update-config")
async def update_configuration(config_update: ConfigUpdate):
    """Update configuration settings"""
    updated_fields = []
    
    for field, value in config_update.dict(exclude_unset=True).items():
        if hasattr(config, field):
            setattr(config, field, value)
            updated_fields.append(field)
    
    return {
        "message": f"Configuration updated: {', '.join(updated_fields)}",
        "updated_config": {
            "START": config.START,
            "NUM_LECS": config.NUM_LECS,
            "MODEL": config.MODEL,
            "GET_TRANSCRIPTS": config.GET_TRANSCRIPTS,
            "GET_KEY_POINTS": config.GET_KEY_POINTS,
            "GET_Q_AND_A": config.GET_Q_AND_A,
            "TRY_REUSE_NOTES": config.TRY_REUSE_NOTES,
            "IS_BOOK": config.IS_BOOK
        }
    }

@router.get("/temp-files")
async def list_temp_files_endpoint():
    """List all files in the temp directory"""
    try:
        files = list_temp_files()
        file_info = []
        for file_path in files:
            file_info.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "created": file_path.stat().st_ctime
            })
        return {"files": file_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing temp files: {str(e)}")

@router.get("/temp-files/{filename}")
async def get_temp_file(filename: str):
    """Serve a file from the temp directory"""
    try:
        file_path = get_temp_file_path(filename)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type based on file extension
        if filename.endswith('.pdf'):
            media_type = 'application/pdf'
        elif filename.endswith('.json'):
            media_type = 'application/json'
        elif filename.endswith('.md'):
            media_type = 'text/markdown'
        else:
            media_type = 'application/octet-stream'
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

@router.get("/temp-files/{filename}/content")
async def get_temp_file_content(filename: str):
    """Get the content of a text file from temp directory as JSON"""
    try:
        file_path = get_temp_file_path(filename)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if filename.endswith('.md'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content, "type": "markdown"}
        elif filename.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content, "type": "json"}
        else:
            raise HTTPException(status_code=400, detail="File type not supported for content viewing")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file content: {str(e)}")
