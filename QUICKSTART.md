# 🚀 Quick Start Guide

Get up and running with Podcast Transcription Archive in 5 minutes!

## Prerequisites

- Python 3.10+
- FFmpeg installed
- 4GB+ RAM

## Installation (5 Steps)

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/podcast-transcription-archive.git
cd podcast-transcription-archive
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env if you want to use cloud APIs (optional)
```

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Start GUI

```bash
python run_gui.py
```

Visit `http://localhost:8501`

### 5. Add Your First Podcast

1. Click **Add Files** in the sidebar
2. Click **Scan Directory** tab
3. Enter path to your podcast folder (e.g., `/home/user/podcasts`)
4. Check **Include subdirectories**
5. Check **Auto-add to queue**
6. Click **Scan Directory**
7. Go to **Queue** tab
8. Click **Start Processing**

## Your First Search

1. Wait for processing to complete
2. Click **Search** in sidebar
3. Enter keywords (e.g., "machine learning")
4. Click **Search**
5. Browse results!

## Export Transcripts

1. Go to **Browse** tab
2. Find an episode
3. Click **Export**
4. Choose format (TXT, SRT, VTT, JSON, Markdown, PDF)
5. Download!

## What's Next?

- Check out the [README](README.md) for full documentation
- Configure cloud APIs for faster processing
- Set up Docker for production deployment
- Explore the API at `http://localhost:8000/docs`

## Troubleshooting

**GUI won't start?**
```bash
pip install streamlit --upgrade
python run_gui.py
```

**Processing stuck?**
- Check the Queue tab for errors
- Make sure FFmpeg is installed: `ffmpeg -version`
- Try a smaller Whisper model in Settings

**Need help?**
- Open an issue on GitHub
- Check the full README
- Join our discussions

Happy transcribing! 🎙️
