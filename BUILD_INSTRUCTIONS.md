# 📦 Complete Build Instructions

## Overview

This document provides comprehensive instructions for building standalone executables of Podcast Transcription Archive.

## 🎯 Build Methods

### Method 1: Automated Build Scripts (Recommended)

**Easiest method** - One command to build everything.

**Windows:**
```batch
build_windows.bat
```

**macOS:**
```bash
./build_macos.sh
```

**Linux:**
```bash
./build_linux.sh
```

### Method 2: Manual PyInstaller

**For advanced users** who want more control.

```bash
# Install build tools
pip install -r requirements-build.txt

# Build with PyInstaller
pyinstaller podcast_archive.spec
```

### Method 3: Direct Python (No Build)

**Skip building** - Run directly with Python.

```bash
python podcast_archive_launcher.py
```

## 🛠️ Prerequisites

### All Platforms

1. **Python 3.10+**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

2. **FFmpeg**
   - Required for audio processing
   - Download: https://ffmpeg.org/download.html
   - Verify: `ffmpeg -version`

3. **Git**
   - To clone repository
   - Download: https://git-scm.com/downloads

### Windows-Specific

- Visual C++ Redistributable (usually pre-installed)
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

### macOS-Specific

- Xcode Command Line Tools
  ```bash
  xcode-select --install
  ```

### Linux-Specific

```bash
sudo apt install python3-dev python3-venv build-essential
```

## 📝 Step-by-Step Build Process

### Step 1: Prepare Environment

```bash
# Clone repository
git clone https://github.com/yourusername/podcast-transcription-archive.git
cd podcast-transcription-archive

# Create virtual environment
python -m venv venv-build

# Activate virtual environment
# Windows:
venv-build\Scripts\activate
# macOS/Linux:
source venv-build/bin/activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install application dependencies
pip install -r requirements.txt

# Install build dependencies
pip install -r requirements-build.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
```

### Step 3: Build Executable

**Windows:**
```batch
pyinstaller ^
    --name "PodcastArchive" ^
    --onefile ^
    --windowed ^
    --add-data "frontend;frontend" ^
    --add-data ".env.example;." ^
    --collect-all streamlit ^
    --collect-all nltk ^
    podcast_archive_launcher.py
```

**macOS:**
```bash
pyinstaller \
    --name "Podcast Archive" \
    --onefile \
    --windowed \
    --add-data "frontend:frontend" \
    --add-data ".env.example:." \
    --collect-all streamlit \
    --collect-all nltk \
    --osx-bundle-identifier "com.podcastarchive.app" \
    podcast_archive_launcher.py
```

**Linux:**
```bash
pyinstaller \
    --name "podcast-archive" \
    --onefile \
    --add-data "frontend:frontend" \
    --add-data ".env.example:." \
    --collect-all streamlit \
    --collect-all nltk \
    podcast_archive_launcher.py
```

### Step 4: Test Executable

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

### Step 5: Create Distribution Package

```bash
# Create distribution folder
mkdir distribution

# Copy executable and docs
# Windows:
copy dist\PodcastArchive.exe distribution\
copy .env.example distribution\
copy README.md distribution\
copy QUICKSTART.md distribution\

# macOS/Linux:
cp dist/podcast-archive distribution/  # or .app
cp .env.example distribution/
cp README.md distribution/
cp QUICKSTART.md distribution/
```

## 🎨 Customization

### Add Custom Icon

**Windows (.ico):**
```batch
pyinstaller --icon="assets/icon.ico" podcast_archive_launcher.py
```

**macOS (.icns):**
```bash
pyinstaller --icon="assets/icon.icns" podcast_archive_launcher.py
```

### Change Application Name

Edit `podcast_archive.spec`:
```python
name='YourCustomName'
```

### Reduce Executable Size

```bash
# Use UPX compression
pyinstaller --upx-dir=/path/to/upx podcast_archive_launcher.py

# Exclude unnecessary packages
pyinstaller --exclude-module matplotlib podcast_archive_launcher.py
```

## 🔍 Advanced Options

### Hidden Imports

If modules are missing, add:
```bash
pyinstaller --hidden-import=module_name podcast_archive_launcher.py
```

### Include Data Files

```bash
pyinstaller --add-data "source:destination" podcast_archive_launcher.py
```

### Console vs Windowed

```bash
# Show console window (debugging)
pyinstaller --console podcast_archive_launcher.py

# Hide console window (production)
pyinstaller --windowed podcast_archive_launcher.py
```

## 📊 Build Metrics

### Expected Build Times

- **First build**: 5-15 minutes
- **Rebuild**: 2-5 minutes
- **Clean build**: 5-10 minutes

### Expected File Sizes

| Platform | Compressed | Uncompressed |
|----------|-----------|--------------|
| Windows  | 150-200MB | 400-600MB    |
| macOS    | 180-220MB | 500-700MB    |
| Linux    | 160-210MB | 450-650MB    |

### Build Artifacts

After building, you'll have:
```
project/
├── build/              # Temporary build files
├── dist/               # Final executable
│   └── PodcastArchive.exe
├── distribution/       # Distribution package
│   ├── PodcastArchive.exe
│   ├── .env.example
│   ├── README.md
│   └── QUICKSTART.md
└── PodcastArchive.spec # Build specification
```

## 🐛 Troubleshooting

### Build Fails with "Module not found"

```bash
# Install missing module
pip install module_name

# Or add hidden import
pyinstaller --hidden-import=module_name podcast_archive_launcher.py
```

### Executable Crashes on Startup

```bash
# Build with console to see errors
pyinstaller --console podcast_archive_launcher.py

# Run and check console output
dist/PodcastArchive.exe
```

### "Permission denied" on macOS

```bash
# Remove quarantine attribute
xattr -cr "dist/Podcast Archive.app"

# Make executable
chmod +x "dist/Podcast Archive.app/Contents/MacOS/Podcast Archive"
```

### Large Executable Size

This is normal! The executable includes:
- Python runtime (~50MB)
- PyTorch (~200MB)
- All dependencies (~150MB)
- Data files (~50MB)

To reduce size:
```bash
# Use one-folder mode instead of one-file
pyinstaller --onedir podcast_archive_launcher.py

# Exclude heavy packages
pyinstaller --exclude-module scipy podcast_archive_launcher.py
```

### Slow Startup

First launch is slower because:
- Extracting bundled files
- Initializing database
- Downloading NLTK data
- Loading AI models

Subsequent launches are faster.

## 🚀 Optimization Tips

### Faster Builds

```bash
# Use spec file (faster rebuilds)
pyinstaller podcast_archive.spec

# Skip UPX compression
pyinstaller --noupx podcast_archive_launcher.py

# Use build cache
# (automatically enabled)
```

### Smaller Executables

```bash
# Exclude unused packages
pyinstaller \
    --exclude-module matplotlib \
    --exclude-module scipy \
    --exclude-module pandas \
    podcast_archive_launcher.py
```

### Better Performance

```bash
# One-folder mode (faster startup)
pyinstaller --onedir podcast_archive_launcher.py

# Optimize bytecode
pyinstaller --optimize 2 podcast_archive_launcher.py
```

## 📦 Creating Installers

### Windows Installer (NSIS)

```bash
# Install NSIS
# Download from https://nsis.sourceforge.io/

# Create installer script
makensis installer.nsi
```

### macOS DMG

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
    --volname "Podcast Archive" \
    --window-size 800 400 \
    --icon-size 100 \
    --app-drop-link 600 185 \
    "PodcastArchive.dmg" \
    "dist/Podcast Archive.app"
```

### Linux AppImage

```bash
# Use AppImage tools
# See: https://appimage.org/
```

## ✅ Quality Checklist

Before distributing:

- [ ] Executable runs without errors
- [ ] GUI opens successfully
- [ ] Can add and process files
- [ ] Search works
- [ ] Export functions work
- [ ] File size is reasonable
- [ ] No console errors
- [ ] Tested on clean system
- [ ] Documentation included
- [ ] Version number correct

## 🎉 Distribution

### Packaging for Distribution

```bash
# Create ZIP file
# Windows:
powershell Compress-Archive -Path distribution\* -DestinationPath PodcastArchive-v1.0-Windows.zip

# macOS/Linux:
zip -r PodcastArchive-v1.0-macOS.zip distribution/
```

### Upload Locations

- GitHub Releases
- Google Drive
- Dropbox
- Your own website
- Cloud storage

### User Requirements

Recipients need:
- **OS**: Windows 10+, macOS 10.13+, Ubuntu 20.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space
- **FFmpeg**: Must be installed separately

## 📞 Support

For build issues:
- Check this guide first
- Review PyInstaller docs: https://pyinstaller.org/
- Open GitHub issue
- Check troubleshooting section

## 🔄 Updates

To rebuild after code changes:

```bash
# Clean old build
rm -rf build dist *.spec

# Rebuild
./build_windows.bat  # or appropriate script
```

## 🎓 Learn More

- PyInstaller: https://pyinstaller.org/
- Python Packaging: https://packaging.python.org/
- Nuitka (alternative): https://nuitka.net/
- Briefcase (alternative): https://briefcase.readthedocs.io/

---

**Happy Building! 🚀**
