"""
Test script to verify the temp directory functionality is working correctly.
"""

import os
import sys
from pathlib import Path

# Add the backend app to the path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

from app.utils.temp_utils import (
    get_temp_dir, 
    create_temp_file, 
    save_temp_file, 
    save_temp_json, 
    save_temp_markdown,
    list_temp_files,
    cleanup_temp_files
)

def test_temp_utils():
    """Test all temp utility functions"""
    print("🧪 Testing temp utilities...")
    
    # Test 1: Get temp directory
    temp_dir = get_temp_dir()
    print(f"✅ Temp directory: {temp_dir}")
    assert temp_dir.exists(), "Temp directory should exist"
    
    # Test 2: Create temp file
    temp_file = create_temp_file(suffix='.txt', prefix='test_', content=b'Hello World!')
    print(f"✅ Created temp file: {temp_file}")
    assert temp_file.exists(), "Temp file should exist"
    
    # Test 3: Save binary file
    pdf_path = save_temp_file(b'%PDF-1.4 fake pdf content', 'test.pdf')
    print(f"✅ Saved PDF file: {pdf_path}")
    assert pdf_path.exists(), "PDF file should exist"
    
    # Test 4: Save JSON file
    test_data = {"lectures": [{"index": 1, "title": "Test Lecture", "content": "Test content"}]}
    json_path = save_temp_json(test_data, 'test_lectures.json')
    print(f"✅ Saved JSON file: {json_path}")
    assert json_path.exists(), "JSON file should exist"
    
    # Test 5: Save markdown file
    markdown_content = """# Test Lecture
    
## Study Notes
This is a test lecture with some **bold** text and *italic* text.

## Key Points
- Point 1
- Point 2
- Point 3
"""
    md_path = save_temp_markdown(markdown_content, 'test_lecture.md')
    print(f"✅ Saved Markdown file: {md_path}")
    assert md_path.exists(), "Markdown file should exist"
    
    # Test 6: List temp files
    temp_files = list_temp_files()
    print(f"✅ Found {len(temp_files)} temp files:")
    for file_path in temp_files:
        print(f"   - {file_path.name} ({file_path.stat().st_size} bytes)")
    
    # Test 7: Read back the files to verify content
    with open(json_path, 'r') as f:
        loaded_data = eval(f.read())  # Using eval for simplicity
        assert loaded_data == test_data, "JSON content should match"
    print("✅ JSON content verified")
    
    with open(md_path, 'r') as f:
        loaded_md = f.read()
        assert "Test Lecture" in loaded_md, "Markdown content should contain title"
    print("✅ Markdown content verified")
    
    # Test 8: Cleanup (optional - comment out to keep files for manual inspection)
    # cleanup_count = cleanup_temp_files()
    # print(f"✅ Cleaned up {cleanup_count} temp files")
    
    print("\n🎉 All tests passed! Temp utilities are working correctly.")
    print(f"📁 Temp files are located at: {temp_dir}")

if __name__ == "__main__":
    test_temp_utils()
