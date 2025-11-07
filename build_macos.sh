#!/bin/bash
# Build script for macOS application bundle using PyInstaller

echo "=========================================="
echo "  Podcast Archive - macOS Build Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv-build" ]; then
    echo "Creating build environment..."
    python3 -m venv venv-build
fi

# Activate virtual environment
echo "Activating build environment..."
source venv-build/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q -r requirements-build.txt

# Download NLTK data
echo "Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build macOS application
echo ""
echo "Building macOS application bundle..."
echo "This may take 5-10 minutes..."
echo ""

pyinstaller \
    --name "Podcast Archive" \
    --onefile \
    --windowed \
    --icon="assets/icon.icns" \
    --add-data "frontend:frontend" \
    --add-data ".env.example:." \
    --hidden-import "streamlit" \
    --hidden-import "backend" \
    --hidden-import "sklearn.utils._cython_blas" \
    --hidden-import "sklearn.neighbors.typedefs" \
    --hidden-import "sklearn.tree._utils" \
    --hidden-import "uvicorn.logging" \
    --hidden-import "uvicorn.loops.auto" \
    --hidden-import "uvicorn.protocols.http.auto" \
    --collect-all "streamlit" \
    --collect-all "nltk" \
    --collect-all "whisper" \
    --osx-bundle-identifier "com.podcastarchive.app" \
    podcast_archive_launcher.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✓ Build successful!"
    echo "=========================================="
    echo ""
    echo "Application location: dist/Podcast Archive.app"
    echo "Size: $(du -sh 'dist/Podcast Archive.app' | cut -f1)"
    echo ""
    echo "To run:"
    echo "  Double-click 'dist/Podcast Archive.app'"
    echo "  Or run: open 'dist/Podcast Archive.app'"
    echo ""

    # Create DMG (requires create-dmg)
    if command -v create-dmg &> /dev/null; then
        echo "Creating DMG installer..."
        create-dmg \
            --volname "Podcast Archive" \
            --window-pos 200 120 \
            --window-size 800 400 \
            --icon-size 100 \
            --app-drop-link 600 185 \
            "dist/PodcastArchive.dmg" \
            "dist/Podcast Archive.app"
        echo "✓ DMG created: dist/PodcastArchive.dmg"
    fi

    # Create distribution folder
    mkdir -p distribution
    cp -r "dist/Podcast Archive.app" distribution/
    cp .env.example distribution/
    cp README.md distribution/
    cp QUICKSTART.md distribution/

    echo "Distribution package created in: distribution/"
    echo ""
else
    echo ""
    echo "❌ Build failed!"
    echo "Check the error messages above."
    exit 1
fi
