#!/bin/bash
# Installation script for Behavioral Authentication System (Linux/Mac)

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  AI-Based Behavioral Authentication System - Setup             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "✅ Python detected:"
python3 --version
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ ERROR: pip3 is not available"
    exit 1
fi

echo "✅ pip3 is available"
echo ""

# Install requirements
echo "📦 Installing required packages..."
echo "This may take 1-2 minutes..."
echo ""

pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERROR: Failed to install packages"
    exit 1
fi

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📚 Next steps:"
echo ""
echo "  1. Run Quick Demo:"
echo "     python3 quick_start.py"
echo ""
echo "  2. Launch Main Application:"
echo "     python3 main_app.py"
echo ""
echo "  3. View Examples:"
echo "     python3 examples.py"
echo ""
echo "  4. Run Tests:"
echo "     python3 test_suite.py"
echo ""
echo ""
echo "📖 Documentation:"
echo "  - README.md: Complete documentation"
echo "  - API_REFERENCE.md: Full API reference"
echo "  - QUICKSTART.txt: Getting started guide"
echo ""
