"""
Example usage of the Auto Lecture App API

This script demonstrates how to use the FastAPI backend to process lecture PDFs.
"""

import requests
import json
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print("❌ API health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return False

def get_status():
    """Get current API configuration"""
    response = requests.get(f"{BASE_URL}/status")
    if response.status_code == 200:
        print("📊 Current Configuration:")
        config = response.json()["config"]
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Failed to get status")

def update_config(updates):
    """Update API configuration"""
    response = requests.post(f"{BASE_URL}/update-config", json=updates)
    if response.status_code == 200:
        print("✅ Configuration updated")
        print(f"📊 Updated fields: {response.json()['message']}")
    else:
        print("❌ Failed to update configuration")
        print(f"Error: {response.text}")

def process_complete_pipeline(pdf_files):
    """Process PDFs through the complete pipeline"""
    if not pdf_files:
        print("❌ No PDF files provided")
        return
    
    files = []
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"❌ File not found: {pdf_file}")
            return
        files.append(('files', (os.path.basename(pdf_file), open(pdf_file, 'rb'), 'application/pdf')))
    
    print(f"🚀 Processing {len(pdf_files)} PDF files...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/process-complete-pipeline",
            files=files,
            data={'max_concurrent': 2}  # Limit concurrent API calls
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Processing completed successfully!")
            print(f"💰 Total cost: ${result['total_cost']:.4f}")
            print(f"📚 Processed lectures: {result['processed_count']}")
            
            # Save results to file
            output_file = "processed_lectures.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Results saved to: {output_file}")
            
            # Print summary of first result
            if result['results']:
                first_result = result['results'][0]
                print(f"\n📖 Sample result - {first_result['title']}:")
                print(f"  Study notes: {len(first_result['study_notes'])} characters")
                if first_result.get('questions'):
                    print(f"  Questions: {len(first_result['questions'])} characters")
                if first_result.get('answers'):
                    print(f"  Answers: {len(first_result['answers'])} characters")
                if first_result.get('key_points'):
                    print(f"  Key points: {len(first_result['key_points'])} characters")
                if first_result.get('transcript'):
                    print(f"  Transcript: {len(first_result['transcript'])} characters")
        else:
            print("❌ Processing failed")
            print(f"Error: {response.text}")
    
    finally:
        # Close file handles
        for _, file_data in files:
            if hasattr(file_data[1], 'close'):
                file_data[1].close()

def main():
    print("🎓 Auto Lecture App - API Example")
    print("=" * 40)
    
    # Test API health
    if not test_health():
        return
    
    # Get current status
    get_status()
    print()
    
    # Example: Update configuration
    print("🔧 Updating configuration...")
    update_config({
        "MODEL": "gpt-4o-mini",
        "GET_TRANSCRIPTS": True,
        "GET_Q_AND_A": True,
        "GET_KEY_POINTS": True,
        "START": 1,
        "NUM_LECS": 5  # Process only first 5 lectures
    })
    print()
    
    # Example: Process PDFs
    # Replace with actual PDF file paths
    pdf_files = [
        # "path/to/your/lecture1.pdf",
        # "path/to/your/lecture2.pdf",
        # "path/to/your/lecture3.pdf"
    ]
    
    if pdf_files:
        process_complete_pipeline(pdf_files)
    else:
        print("ℹ️  To process PDFs, update the 'pdf_files' list with your PDF file paths")
        print("   Example:")
        print('   pdf_files = ["lecture1.pdf", "lecture2.pdf"]')

if __name__ == "__main__":
    main()
