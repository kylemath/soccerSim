#!/bin/bash
# Setup script for soccer simulation project

echo "Setting up 7x7 Soccer Simulation..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete! To activate the virtual environment, run:"
echo "source venv/bin/activate"
echo ""
echo "Then run the app with:"
echo "python app.py"

