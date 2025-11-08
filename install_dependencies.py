#!/usr/bin/env python3
"""
Dependency installation script for AI Research Assistant
Handles platform-specific installation issues
"""

import sys
import subprocess
import platform
import os

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system().lower()
    
    if system == 'linux':
        # Ubuntu/Debian
        return run_command(
            "sudo apt-get update && sudo apt-get install -y "
            "libxml2-dev libxslt-dev libjpeg-dev zlib1g-dev",
            "Installing system dependencies (Linux)"
        )
    elif system == 'darwin':  # macOS
        return run_command(
            "brew update && brew install libxml2 libxslt jpeg zlib",
            "Installing system dependencies (macOS)"
        )
    elif system == 'windows':
        print("ℹ️  On Windows, system dependencies are usually handled automatically")
        return True
    else:
        print(f"⚠️  Unsupported system: {system}")
        return True

def install_python_dependencies():
    """Install Python dependencies"""
    steps = [
        ("python -m pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing Python dependencies")
    ]
    
    all_success = True
    for cmd, description in steps:
        if not run_command(cmd, description):
            all_success = False
    
    return all_success

def verify_installation():
    """Verify that installation was successful"""
    print("🔍 Verifying installation...")
    
    try:
        # Test critical imports
        import streamlit
        import chromadb
        import fitz  # PyMuPDF
        import google.generativeai
        
        print("✅ Critical dependencies imported successfully")
        
        # Test our modules
        from agents.pdf_parser import PDFParserAgent
        from agents.rag_agent import RAGAgent
        from utils.database import PaperDatabase
        
        print("✅ Project modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import verification failed: {e}")
        return False

def main():
    print("🚀 AI Research Assistant - Dependency Installation")
    print("=" * 50)
    
    # Install system dependencies
    if not install_system_dependencies():
        print("❌ System dependency installation failed")
        return 1
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Python dependency installation failed")
        return 1
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        return 1
    
    print("\n🎉 Installation completed successfully!")
    print("\n📝 Next steps:")
    print("1. Copy .env.example to .env")
    print("2. Add your Gemini API key to .env")
    print("3. Run: streamlit run app.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())