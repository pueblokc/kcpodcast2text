# 🚀 One-Click Build Guide

This guide will help you create a standalone executable that doesn't require Python installation.

## 🎯 Quick Build

### Windows

```batch
# Double-click this file or run in Command Prompt:
build_windows.bat
```

The executable will be created at: `dist/PodcastArchive.exe`

### macOS

```bash
# Run in Terminal:
chmod +x build_macos.sh
./build_macos.sh
```

The app will be created at: `dist/Podcast Archive.app`

### Linux

```bash
# Run in Terminal:
chmod +x build_linux.sh
./build_linux.sh
```

The executable will be created at: `dist/podcast-archive`

## 📋 Requirements for Building

Before building, you need:

1. **Python 3.10 or higher** installed
2. **Git** (to clone the repository)
3. **FFmpeg** installed on your system

### Installing Python

**Windows:**
- Download from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

**macOS:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt install python3.11 python3.11-venv
```

### Installing FFmpeg

**Windows:**
- Download from https://ffmpeg.org/download.html
- Add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

## 🔨 Detailed Build Process

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/podcast-transcription-archive.git
cd podcast-transcription-archive
```

### Step 2: Run Build Script

**Windows:**
```batch
build_windows.bat
```

**macOS/Linux:**
```bash
./build_macos.sh    # macOS
./build_linux.sh    # Linux
```

### Step 3: Find Your Executable

The build process creates a `distribution/` folder with:
- The executable file
- Configuration file (`.env.example`)
- Documentation (README, QUICKSTART)

**Windows:** `distribution/PodcastArchive.exe`
**macOS:** `distribution/Podcast Archive.app`
**Linux:** `distribution/podcast-archive`

## 📦 Distribution Package

After building, you'll have a complete distribution package in the `distribution/` folder:

```
distribution/
├── PodcastArchive.exe (or .app, or binary)
├── .env.example
├── README.md
└── QUICKSTART.md
```

You can:
1. Zip this folder
2. Share it with others
3. They can run it without installing Python!

## ⚡ Quick Run (Without Building)

If you don't want to build an executable, you can run directly:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the launcher
python podcast_archive_launcher.py
```

## 🐛 Troubleshooting Build Issues

### "Python not found"
- Install Python 3.10+
- Add Python to system PATH

### "pip not found"
- Run: `python -m ensurepip --upgrade`

### Build takes too long (>15 minutes)
- This is normal for the first build
- PyInstaller needs to bundle all dependencies
- Subsequent builds are faster

### "Missing module" errors
- Make sure you ran: `pip install -r requirements.txt`
- Try: `pip install -r requirements-build.txt`

### Executable is very large (>500MB)
- This is normal! It includes:
  - Python runtime
  - All libraries (Whisper, Streamlit, etc.)
  - NLTK data
  - Everything needed to run offline

### Windows Defender blocks the .exe
- This is normal for unsigned executables
- Click "More info" → "Run anyway"
- Or add exception in Windows Defender

### macOS says "App is damaged"
- Run: `xattr -cr "dist/Podcast Archive.app"`
- Or: Right-click → Open → Click "Open"

## 🎁 Pre-built Executables

**Not available yet** - You'll need to build it yourself.

## 📊 Build Output Size

Expected sizes:
- **Windows**: ~400-600 MB
- **macOS**: ~500-700 MB
- **Linux**: ~450-650 MB

This is normal! The executable includes:
- Python runtime (~50MB)
- PyTorch + Whisper models (~200MB)
- Streamlit + dependencies (~100MB)
- All other libraries (~100MB)

## 🎯 What Gets Bundled

The executable includes:
✅ Python runtime
✅ All Python packages
✅ Whisper AI model (small)
✅ NLTK data
✅ Streamlit GUI
✅ FastAPI backend
✅ SQLite database engine
✅ All dependencies

The executable does NOT include:
❌ Large Whisper models (downloaded on first use)
❌ Your podcast files
❌ Transcripts database (created on first run)

## 💡 Tips

1. **First build is slowest** - Be patient!
2. **Test the executable** - Run it before distributing
3. **Include FFmpeg** - Recipients need FFmpeg installed
4. **Check file size** - Should be 400-700MB
5. **Antivirus warnings** - Normal for PyInstaller executables

## 🔄 Rebuild After Changes

If you modify the code:

```bash
# Clean previous build
rm -rf build dist

# Rebuild
./build_windows.bat  # or build_macos.sh, build_linux.sh
```

## ✅ Verification

After building, test the executable:

**Windows:**
```batch
dist\PodcastArchive.exe
```

**macOS:**
```bash
open "dist/Podcast Archive.app"
```

**Linux:**
```bash
./dist/podcast-archive
```

You should see:
1. Console window with startup messages
2. Browser opens to http://localhost:8501
3. Streamlit GUI loads successfully

## 🎉 Success!

Once built, you can:
- Share the `distribution/` folder
- Create a ZIP file
- Upload to cloud storage
- Distribute to users without Python

Recipients just need:
- Windows 10+, macOS 10.13+, or Linux
- FFmpeg installed
- 4GB+ RAM

That's it! No Python, no pip, no dependencies! 🚀
