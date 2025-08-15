"""
Output file utilities for managing final output files.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Union
from contextlib import contextmanager

# Define the project outputs directory
PROJECT_OUTPUTS_DIR = Path(__file__).parent.parent.parent.parent / "outputs"

def get_outputs_dir() -> Path:
    """Get the project outputs directory, creating it if it doesn't exist."""
    PROJECT_OUTPUTS_DIR.mkdir(exist_ok=True)
    return PROJECT_OUTPUTS_DIR

def save_output_markdown(content: str, filename: str) -> Path:
    """
    Save markdown content to an output file in the project outputs directory.
    
    Args:
        content: Markdown content as string
        filename: Desired filename
        
    Returns:
        Path to the saved markdown file
    """
    outputs_dir = get_outputs_dir()
    file_path = outputs_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

def save_output_json(data: dict, filename: str) -> Path:
    """
    Save JSON data to an output file in the project outputs directory.
    
    Args:
        data: Dictionary to save as JSON
        filename: Desired filename
        
    Returns:
        Path to the saved JSON file
    """
    import json
    outputs_dir = get_outputs_dir()
    file_path = outputs_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return file_path

def list_output_files() -> list[Path]:
    """
    List all files in the outputs directory.
    
    Returns:
        List of file paths in the outputs directory
    """
    outputs_dir = get_outputs_dir()
    return [f for f in outputs_dir.iterdir() if f.is_file()]

def get_output_file_path(filename: str) -> Path:
    """
    Get the path to a file in the outputs directory.
    
    Args:
        filename: Name of the file
        
    Returns:
        Path to the file in outputs directory
    """
    outputs_dir = get_outputs_dir()
    return outputs_dir / filename

def cleanup_output_files(pattern: str = "*") -> int:
    """
    Clean up output files matching the pattern.
    
    Args:
        pattern: Glob pattern for files to delete (default: all files)
        
    Returns:
        Number of files deleted
    """
    outputs_dir = get_outputs_dir()
    deleted_count = 0
    
    for file_path in outputs_dir.glob(pattern):
        if file_path.is_file():
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception:
                pass  # Ignore errors during cleanup
    
    return deleted_count
