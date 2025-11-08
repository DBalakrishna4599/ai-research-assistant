#!/usr/bin/env python3
"""
Compatibility check script for AI Research Assistant
Checks if all dependencies can be imported and work together
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("❌ Python 3.8 or higher required")
        return False
    else:
        print("✅ Python version compatible")
        return True

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        if package_name:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                raise ImportError(f"Module {module_name} not found")
        else:
            __import__(module_name)
        print(f"✅ {module_name} can be imported")
        return True
    except ImportError as e:
        print(f"❌ {module_name} import failed: {e}")
        return False

def check_dependencies():
    """Check all required dependencies"""
    dependencies = [
        "streamlit",
        "chromadb", 
        "fitz",  # PyMuPDF
        "dotenv",
        "google.generativeai",
        "numpy",
        "pandas",
        "sklearn",
        "sentence_transformers",
        "plotly",
        "requests", 
        "tqdm",
        "nltk"
    ]
    
    all_imports_ok = True
    for dep in dependencies:
        if not check_import(dep):
            all_imports_ok = False
    
    return all_imports_ok

def check_our_modules():
    """Check if our project modules can be imported"""
    our_modules = [
        ("agents.pdf_parser", "PDFParserAgent"),
        ("agents.rag_agent", "RAGAgent"), 
        ("agents.summarizer", "SummarizerAgent"),
        ("utils.database", "PaperDatabase")
    ]
    
    all_ok = True
    for module_path, class_name in our_modules:
        try:
            # Add project root to path
            sys.path.append('.')
            module = __import__(module_path, fromlist=[class_name])
            class_obj = getattr(module, class_name)
            print(f"✅ {module_path}.{class_name} can be imported")
        except Exception as e:
            print(f"❌ {module_path}.{class_name} import failed: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("🔍 AI Research Assistant - Compatibility Check")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Checking dependencies...")
    deps_ok = check_dependencies()
    
    print("\n🏗️ Checking project modules...") 
    modules_ok = check_our_modules()
    
    print("\n" + "=" * 50)
    if deps_ok and modules_ok:
        print("🎉 All compatibility checks passed!")
        return 0
    else:
        print("❌ Some compatibility checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())