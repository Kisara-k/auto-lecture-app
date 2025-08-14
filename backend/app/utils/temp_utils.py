"""
Temporary file utilities for managing files in the local temp directory.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Union
from contextlib import contextmanager

# Define the project temp directory
PROJECT_TEMP_DIR = Path(__file__).parent.parent.parent.parent / "temp"

def get_temp_dir() -> Path:
    """Get the project temp directory, creating it if it doesn't exist."""
    PROJECT_TEMP_DIR.mkdir(exist_ok=True)
    return PROJECT_TEMP_DIR

def create_temp_file(suffix: str = "", prefix: str = "temp_", content: Optional[bytes] = None) -> Path:
    """
    Create a temporary file in the project temp directory.
    
    Args:
        suffix: File extension (e.g., '.pdf', '.json')
        prefix: File prefix for identification
        content: Optional content to write to the file
        
    Returns:
        Path to the created temporary file
    """
    temp_dir = get_temp_dir()
    filename = f"{prefix}{uuid.uuid4().hex}{suffix}"
    temp_file_path = temp_dir / filename
    
    if content is not None:
        with open(temp_file_path, 'wb') as f:
            f.write(content)
    
    return temp_file_path

def save_temp_file(content: bytes, filename: str) -> Path:
    """
    Save content to a named temporary file in the project temp directory.
    
    Args:
        content: File content as bytes
        filename: Desired filename
        
    Returns:
        Path to the saved file
    """
    temp_dir = get_temp_dir()
    file_path = temp_dir / filename
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return file_path

def save_temp_json(data: dict, filename: str) -> Path:
    """
    Save JSON data to a temporary file in the project temp directory.
    
    Args:
        data: Dictionary to save as JSON
        filename: Desired filename
        
    Returns:
        Path to the saved JSON file
    """
    import json
    temp_dir = get_temp_dir()
    file_path = temp_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return file_path

def save_temp_markdown(content: str, filename: str) -> Path:
    """
    Save markdown content to a temporary file in the project temp directory.
    
    Args:
        content: Markdown content as string
        filename: Desired filename
        
    Returns:
        Path to the saved markdown file
    """
    temp_dir = get_temp_dir()
    file_path = temp_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

@contextmanager
def temp_file_context(suffix: str = "", prefix: str = "temp_", delete_on_exit: bool = True):
    """
    Context manager for creating temporary files.
    
    Args:
        suffix: File extension
        prefix: File prefix
        delete_on_exit: Whether to delete the file when exiting the context
        
    Yields:
        Path to the temporary file
    """
    temp_file_path = create_temp_file(suffix=suffix, prefix=prefix)
    try:
        yield temp_file_path
    finally:
        if delete_on_exit and temp_file_path.exists():
            temp_file_path.unlink()

def cleanup_temp_files(pattern: str = "*") -> int:
    """
    Clean up temporary files matching the pattern.
    
    Args:
        pattern: Glob pattern for files to delete (default: all files)
        
    Returns:
        Number of files deleted
    """
    temp_dir = get_temp_dir()
    deleted_count = 0
    
    for file_path in temp_dir.glob(pattern):
        if file_path.is_file():
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception:
                pass  # Ignore errors during cleanup
    
    return deleted_count

def get_temp_file_path(filename: str) -> Path:
    """
    Get the path to a file in the temp directory.
    
    Args:
        filename: Name of the file
        
    Returns:
        Path to the file in temp directory
    """
    temp_dir = get_temp_dir()
    return temp_dir / filename

def list_temp_files() -> list[Path]:
    """
    List all files in the temp directory.
    
    Returns:
        List of file paths in the temp directory
    """
    temp_dir = get_temp_dir()
    return [f for f in temp_dir.iterdir() if f.is_file()]
