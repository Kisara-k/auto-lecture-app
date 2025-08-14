# Auto Lecture App - Frontend

A simple, interactive HTML frontend for testing the Auto Lecture App FastAPI backend.

## Features

### 🎯 **Core Functionality**

- **Drag & Drop Upload**: Upload multiple PDF files with drag-and-drop support
- **Real-time Configuration**: Adjust AI model, processing options, and parameters
- **Complete Pipeline Processing**: End-to-end processing from PDFs to study materials
- **Live Results Display**: View generated content with cost tracking
- **API Status Monitoring**: Real-time backend connection status

### 📱 **User Interface**

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern Styling**: Clean, professional interface with gradients and animations
- **Real-time Feedback**: Loading indicators, status messages, and progress updates
- **File Management**: Add/remove files, view file sizes, and validation
- **Results Export**: Download processed results as JSON

### ⚙️ **Configuration Options**

- **AI Model Selection**: Choose between GPT-4o, GPT-4o-mini, etc.
- **Processing Controls**: Enable/disable transcripts, Q&A, key points
- **Batch Settings**: Configure concurrent API calls and lecture ranges
- **Content Type**: Switch between lecture and book processing modes

## Quick Start

### 1. Start the Backend

First, make sure the FastAPI backend is running:

```bash
cd ../backend
python main.py
```

The backend should be available at `http://localhost:8000`

### 2. Start the Frontend

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh

# Or manually
python serve.py
```

The frontend will be available at `http://localhost:3000`

### 3. Use the Application

1. **Upload PDFs**: Drag and drop or click to select PDF files
2. **Configure Settings**: Adjust AI model and processing options
3. **Process**: Click "Process Complete Pipeline"
4. **View Results**: See generated study materials and download results

## Screenshots

### Main Interface

- Clean upload area with drag-and-drop support
- Configuration panel with all processing options
- Real-time API status indicator

### Results Display

- Organized display of study notes, transcripts, questions, and key points
- Cost tracking per lecture and total
- Downloadable JSON results

## File Structure

```
frontend/
├── index.html          # Main HTML file with embedded CSS/JS
├── serve.py           # Simple HTTP server for development
├── start.bat          # Windows startup script
├── start.sh           # Linux/Mac startup script
└── README.md          # This file
```

## Technical Details

### **HTML Structure**

- Single-page application with all functionality in one file
- Embedded CSS and JavaScript for easy deployment
- Responsive design with CSS Grid and Flexbox

### **JavaScript Features**

- **File Handling**: Drag-and-drop, validation, and management
- **API Communication**: Fetch API for backend communication
- **Real-time Updates**: Status monitoring and progress indicators
- **Error Handling**: Comprehensive error catching and user feedback

### **Styling**

- **Modern Design**: Gradient backgrounds, smooth animations
- **Mobile-First**: Responsive design that works on all devices
- **Visual Feedback**: Hover effects, loading spinners, status colors

## API Integration

The frontend communicates with these backend endpoints:

- `GET /health` - API health check
- `GET /api/v1/status` - Get current configuration
- `POST /api/v1/update-config` - Update processing settings
- `POST /api/v1/process-complete-pipeline` - Complete processing pipeline

## Configuration Options

### **AI Models**

- **gpt-4o-mini**: Recommended for cost-effective processing
- **gpt-4o**: Higher quality but more expensive
- **gpt-4.1-mini**: Alternative model option

### **Processing Options**

- **Generate Transcripts**: Create natural language lecture transcripts
- **Generate Q&A**: Create multiple choice questions with detailed answers
- **Generate Key Points**: Extract essential facts and concepts
- **Book Mode**: Optimize prompts for book content vs. lectures

### **Batch Settings**

- **Start Lecture #**: First lecture to process (useful for large sets)
- **Number of Lectures**: Maximum lectures to process
- **Max Concurrent Calls**: Control API rate limiting (1-10)

## Development

### **Adding Features**

1. **New UI Elements**: Add HTML in the appropriate section
2. **Styling**: Update the embedded CSS styles
3. **Functionality**: Add JavaScript functions
4. **API Calls**: Use the existing fetch patterns

### **Customization**

- **Colors**: Modify CSS custom properties for theming
- **Layout**: Adjust CSS Grid and Flexbox layouts
- **API Base URL**: Change `API_BASE` constant for different backend URLs

### **Deployment**

For production deployment:

1. **Static Hosting**: Upload `index.html` to any static host
2. **Backend URL**: Update API_BASE to production backend URL
3. **CORS**: Ensure backend CORS settings allow frontend domain

## Troubleshooting

### **Common Issues**

**API Offline Error**

- Ensure backend is running on `http://localhost:8000`
- Check if OpenAI API key is configured in backend `.env`
- Verify no firewall blocking local connections

**File Upload Fails**

- Check file is a valid PDF
- Ensure file size is reasonable (< 50MB recommended)
- Try uploading one file at a time

**Processing Errors**

- Check backend logs for detailed error messages
- Verify OpenAI API key has sufficient credits
- Reduce concurrent calls if rate limiting occurs

**CORS Errors**

- Use the provided `serve.py` server for local development
- Don't open `index.html` directly in browser (use HTTP server)

### **Browser Support**

- Chrome 60+ (recommended)
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Notes

- **File Size**: Large PDFs may take longer to upload and process
- **Concurrent Processing**: Higher values may hit rate limits
- **Memory Usage**: Browser may use significant memory for large results
- **Network**: Ensure stable internet connection for API calls

## Future Enhancements

Potential improvements:

- **Progress Tracking**: Real-time processing progress
- **Result Filtering**: Filter/search through results
- **Batch Upload**: ZIP file upload support
- **Export Options**: PDF/Word export of results
- **User Accounts**: Save/load configurations and results
