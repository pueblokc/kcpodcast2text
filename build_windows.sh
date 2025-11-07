#!/bin/bash
# Build script for Windows executable using PyInstaller

echo "=========================================="
echo "  Podcast Archive - Windows Build Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi

echo "✓ Python found: $(python --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv-build" ]; then
    echo "Creating build environment..."
    python -m venv venv-build
fi

# Activate virtual environment
echo "Activating build environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv-build/Scripts/activate
else
    source venv-build/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q -r requirements-build.txt

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build executable
echo ""
echo "Building Windows executable..."
echo "This may take 5-10 minutes..."
echo ""

pyinstaller \
    --name "PodcastArchive" \
    --onefile \
    --windowed \
    --icon="assets/icon.ico" \
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
    podcast_archive_launcher.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✓ Build successful!"
    echo "=========================================="
    echo ""
    echo "Executable location: dist/PodcastArchive.exe"
    echo "Size: $(du -h dist/PodcastArchive.exe | cut -f1)"
    echo ""
    echo "To run:"
    echo "  Windows: double-click dist/PodcastArchive.exe"
    echo "  Or run: ./dist/PodcastArchive.exe"
    echo ""

    # Create distribution folder
    mkdir -p distribution
    cp dist/PodcastArchive.exe distribution/
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
