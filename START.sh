#!/bin/bash
# Quick launcher for macOS/Linux

echo "Starting Podcast Archive..."

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 podcast_archive_launcher.py
