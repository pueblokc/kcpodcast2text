#!/bin/bash
# Build script for Linux AppImage using PyInstaller

echo "=========================================="
echo "  Podcast Archive - Linux Build Script"
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

# Build Linux executable
echo ""
echo "Building Linux executable..."
echo "This may take 5-10 minutes..."
echo ""

pyinstaller \
    --name "podcast-archive" \
    --onefile \
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
    echo "Executable location: dist/podcast-archive"
    echo "Size: $(du -h dist/podcast-archive | cut -f1)"
    echo ""
    echo "To run:"
    echo "  ./dist/podcast-archive"
    echo ""

    # Make executable
    chmod +x dist/podcast-archive

    # Create distribution folder
    mkdir -p distribution
    cp dist/podcast-archive distribution/
    cp .env.example distribution/
    cp README.md distribution/
    cp QUICKSTART.md distribution/

    # Create a desktop entry
    cat > distribution/podcast-archive.desktop << EOF
[Desktop Entry]
Name=Podcast Archive
Comment=Podcast Transcription and Search System
Exec=/path/to/podcast-archive
Icon=podcast-archive
Terminal=false
Type=Application
Categories=AudioVideo;Audio;
EOF

    echo "Distribution package created in: distribution/"
    echo ""
    echo "To install:"
    echo "  sudo cp dist/podcast-archive /usr/local/bin/"
    echo "  sudo cp distribution/podcast-archive.desktop /usr/share/applications/"
    echo ""
else
    echo ""
    echo "❌ Build failed!"
    echo "Check the error messages above."
    exit 1
fi
