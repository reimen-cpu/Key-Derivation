#!/bin/bash

# Stop execution if an error occurs
set -e

echo "================================================="
echo "   PyInstaller Compiler (OneDir) - Key-Derivation   "
echo "================================================="

# Check if inside virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️ WARNING: You are not inside a virtual environment."
    echo "Please cancel (Ctrl+C) and run:"
    echo "   source venv/bin/activate"
    echo ""
    sleep 3
fi

# Install PyInstaller
if ! python3 -m PyInstaller --version &> /dev/null; then
    echo "⚙️  Installing PyInstaller locally..."
    python3 -m pip install pyinstaller
fi

echo "🚀 Starting compilation (OneDir Mode)..."

rm -rf build/ dist/ "Key-Derivation-Portable.spec"

# PyInstaller Options
# --onedir  : Extract into a portable folder structure instead of a single file
# --windowed: No console, pure GUI
python3 -m PyInstaller --noconfirm \
    --onedir \
    --windowed \
    --name "Key-Derivation-Portable" \
    --hidden-import "cryptography" \
    --hidden-import "customtkinter" \
    src/Key-Derivation.py

echo "================================================="
echo "✅ Compilation Successfully Completed!"
echo "📂 Your portable directory is located at: ./dist/Key-Derivation-Portable"
echo "================================================="
