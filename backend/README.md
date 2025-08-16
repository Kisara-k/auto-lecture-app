# FastAPI Backend for Auto Lecture App

This FastAPI backend converts the existing Python scripts into a REST API for processing lecture PDFs and generating study materials using OpenAI.

## Features

- **PDF Merging**: Merge multiple PDF files into a single document with bookmarks
- **Content Extraction**: Extract structured content from PDFs using table of contents
- **AI Processing**: Generate study notes, transcripts, questions, answers, and key points using OpenAI
- **Complete Pipeline**: End-to-end processing from multiple PDFs to study materials
- **Configurable**: Adjust processing parameters via API

## Setup

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the server**:

   ```bash
   python main.py
   ```

   Or with uvicorn directly:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Core Endpoints

- `POST /api/v1/merge-pdfs` - Merge multiple PDF files
- `POST /api/v1/extract-content` - Extract content from merged PDF
- `POST /api/v1/process-lectures` - Process lectures with AI
- `POST /api/v1/process-complete-pipeline` - Complete end-to-end processing

### Configuration

- `GET /api/v1/status` - Get current configuration
- `POST /api/v1/update-config` - Update processing settings

### Utility

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Usage Examples

### Complete Pipeline (Recommended)

Upload multiple PDFs and get fully processed study materials:

```bash
curl -X POST "http://localhost:8000/api/v1/process-complete-pipeline" \
  -F "files=@lecture1.pdf" \
  -F "files=@lecture2.pdf" \
  -F "files=@lecture3.pdf" \
  -F "max_concurrent=3"
```

### Step-by-Step Processing

1. **Merge PDFs**:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/merge-pdfs" \
     -F "files=@lecture1.pdf" \
     -F "files=@lecture2.pdf"
   ```

2. **Extract Content**:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/extract-content" \
     -F "file=@merged_lectures.pdf"
   ```

3. **Process with AI**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/process-lectures" \
     -F "lectures_json=$(cat lectures.json)" \
     -F "max_concurrent=3"
   ```

### Configuration

Update processing settings:

```bash
curl -X POST "http://localhost:8000/api/v1/update-config" \
  -H "Content-Type: application/json" \
  -d '{
    "MODEL": "gpt-4o-mini",
    "GET_TRANSCRIPTS": true,
    "GET_Q_AND_A": true,
    "GET_KEY_POINTS": true,
    "START": 1,
    "NUM_LECS": 10
  }'
```

## Configuration Options

- `START`: Starting lecture index (default: 0)
- `NUM_LECS`: Number of lectures to process (default: 100)
- `MODEL`: OpenAI model to use (default: "gpt-4o-mini")
- `GET_TRANSCRIPTS`: Generate lecture transcripts (default: true)
- `GET_KEY_POINTS`: Generate key points (default: true)
- `GET_Q_AND_A`: Generate questions and answers (default: true)
- `TRY_REUSE_NOTES`: Try to reuse existing notes (default: false)
- `IS_BOOK`: Content is from a book rather than lectures (default: false)

## Response Format

### Processed Lecture Response

```json
{
  "message": "Lectures processed successfully",
  "total_cost": 0.0234,
  "processed_count": 3,
  "results": [
    {
      "index": 1,
      "title": "Introduction to Machine Learning",
      "study_notes": "## 1. Introduction to Machine Learning...",
      "transcript": "Welcome to our comprehensive introduction...",
      "questions": "### 1. What is the primary goal of machine learning?...",
      "answers": "### 1. What is the primary goal of machine learning?\nA) ✓ To enable computers to learn...",
      "key_points": "### 1. Core Concepts\n- Machine learning enables...",
      "cost": 0.0078
    }
  ]
}
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input data or file format
- **429 Too Many Requests**: OpenAI rate limit exceeded
- **500 Internal Server Error**: Processing errors

## Development

### Project Structure

```
backend/
├── app/
│   ├── config.py              # Configuration and prompts
│   ├── models.py              # Pydantic models
│   ├── routers/
│   │   └── lectures.py        # API endpoints
│   └── services/
│       ├── pdf_merger.py      # PDF merging logic
│       ├── content_extractor.py # Content extraction
│       └── openai_service.py  # AI processing
├── main.py                    # FastAPI app
├── requirements.txt           # Dependencies
└── .env.example              # Environment variables template
```

### Adding New Features

1. Add new service functions in `app/services/`
2. Define request/response models in `app/models.py`
3. Create endpoints in `app/routers/lectures.py`
4. Update configuration in `app/config.py` if needed

## Production Deployment

For production deployment:

1. Set proper CORS origins in `main.py`
2. Use a production WSGI server like Gunicorn
3. Set up proper logging and monitoring
4. Configure rate limiting for API endpoints
5. Use environment-specific configuration
