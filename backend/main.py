from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routers import lectures

app = FastAPI(
    title="Auto Lecture App API",
    description="API for processing lecture PDFs and generating study materials using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lectures.router, prefix="/api/v1", tags=["lectures"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Auto Lecture App API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "merge_pdfs": "/api/v1/merge-pdfs",
            "extract_content": "/api/v1/extract-content", 
            "process_lectures": "/api/v1/process-lectures",
            "complete_pipeline": "/api/v1/process-complete-pipeline",
            "status": "/api/v1/status",
            "update_config": "/api/v1/update-config"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
