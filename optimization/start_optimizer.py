#!/usr/bin/env python3
"""
Quick start script for the optimization web interface
"""

import os
import sys
import subprocess

def main():
    print("\n" + "="*60)
    print("Soccer Simulator Optimization Web Interface")
    print("="*60)
    
    # Check if virtual environment exists
    venv_python = os.path.join('venv', 'bin', 'python')
    if not os.path.exists(venv_python):
        print("\n⚠️  Virtual environment not found!")
        print("Please run: source venv/bin/activate")
        print("Or install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    # Activate venv and run the app
    print("\n🚀 Starting web server...")
    print("\n📍 Open your browser and go to: http://127.0.0.1:5001")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    
    try:
        # Run the optimizer app
        subprocess.run([venv_python, 'optimizer_app.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

