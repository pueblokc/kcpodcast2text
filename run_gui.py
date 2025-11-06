#!/usr/bin/env python3
"""
Quick start script for Streamlit GUI
"""
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    print("Starting Podcast Transcription Archive GUI...")
    print("GUI will be available at: http://localhost:8501")
    print("\nPress Ctrl+C to stop the server\n")

    import streamlit.web.cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        str(Path(__file__).parent / "frontend" / "streamlit_app.py"),
        "--server.port=8501",
        "--server.address=localhost",
    ]
    sys.exit(stcli.main())
