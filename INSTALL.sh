#!/bin/bash
# One-click installer for macOS/Linux

echo "=========================================="
echo "  Podcast Archive - Installer"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    PYTHON="python3"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    PYTHON="python3"
else
    OS="Unknown"
    PYTHON="python"
fi

echo "Detected OS: $OS"

# Check Python
if ! command -v $PYTHON &> /dev/null; then
    echo "❌ Python not installed!"
    echo ""
    echo "Please install Python 3.10+"
    echo ""
    if [[ "$OS" == "macOS" ]]; then
        echo "Install with Homebrew:"
        echo "  brew install python@3.11"
    elif [[ "$OS" == "Linux" ]]; then
        echo "Install with apt:"
        echo "  sudo apt install python3.11 python3.11-venv"
    fi
    exit 1
fi

echo "[1/5] ✓ Python found"
$PYTHON --version

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo ""
    echo "Installing pip..."
    $PYTHON -m ensurepip --upgrade
fi

# Create virtual environment
echo "[2/5] Creating virtual environment..."
$PYTHON -m venv venv
source venv/bin/activate

# Install dependencies
echo "[3/5] Installing dependencies (this may take a few minutes)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Download NLTK data
echo "[4/5] Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

# Initialize database
echo "[5/5] Initializing database..."
python scripts/init_db.py

echo ""
echo "=========================================="
echo "  ✓ Installation Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo "  2. Run the GUI:"
echo "     python run_gui.py"
echo ""
echo "Or use the quick launcher:"
echo "  ./START.sh"
echo ""
