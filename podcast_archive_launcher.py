#!/usr/bin/env python3
"""
Simplified launcher for Podcast Transcription Archive
Launches the Streamlit GUI with all necessary setup
"""
import sys
import os
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

# Add current directory to path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = Path(sys.executable).parent
else:
    # Running as script
    application_path = Path(__file__).parent

sys.path.insert(0, str(application_path))

# Set environment variables
os.environ['PYTHONPATH'] = str(application_path)


def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import streamlit
        import fastapi
        import sqlalchemy
        import whisper
        import nltk
        print("✓ All dependencies loaded successfully")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False


def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        print("✓ NLTK data ready")
    except Exception as e:
        print(f"⚠ NLTK download warning: {e}")


def init_database():
    """Initialize database if needed"""
    import asyncio
    from backend.database import init_db

    db_path = application_path / 'data' / 'podcasts.db'

    if not db_path.exists():
        print("Initializing database...")
        asyncio.run(init_db())
        print("✓ Database initialized")
    else:
        print("✓ Database exists")


def start_backend():
    """Start FastAPI backend in background"""
    from backend.main import app
    import uvicorn

    print("Starting backend API...")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="error",
    )


def start_frontend():
    """Start Streamlit frontend"""
    import streamlit.web.cli as stcli

    print("Starting Podcast Archive GUI...")
    print("\n" + "="*60)
    print("  🎙️  PODCAST TRANSCRIPTION ARCHIVE")
    print("="*60)
    print("\n✓ Application starting...")
    print("✓ Opening browser...")
    print("\nGUI URL: http://localhost:8501")
    print("API URL: http://localhost:8000")
    print("\nPress Ctrl+C to stop the application\n")

    sys.argv = [
        "streamlit",
        "run",
        str(application_path / "frontend" / "streamlit_app.py"),
        "--server.port=8501",
        "--server.address=127.0.0.1",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]

    sys.exit(stcli.main())


def main():
    """Main launcher"""
    print("="*60)
    print("  🎙️  Podcast Transcription Archive - Launcher")
    print("="*60)
    print()

    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Setup incomplete. Please run: pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Download NLTK data
    download_nltk_data()

    # Initialize database
    try:
        init_database()
    except Exception as e:
        print(f"⚠ Database initialization warning: {e}")

    # Create necessary directories
    for dir_name in ['data', 'data/temp', 'data/transcripts', 'models']:
        dir_path = application_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

    print("✓ All systems ready\n")

    # Start backend in background thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Wait a moment for backend to start
    time.sleep(2)

    # Start frontend (this blocks)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print("✓ Application stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
