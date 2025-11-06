#!/usr/bin/env python3
"""
Quick start script for backend API server
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.main import main

if __name__ == "__main__":
    print("Starting Podcast Transcription Archive Backend...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    main()
