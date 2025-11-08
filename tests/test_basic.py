import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_python_version():
    """Test Python version compatibility"""
    version = sys.version_info
    assert version >= (3, 8), "Python 3.8 or higher required"

def test_imports():
    """Test that all modules can be imported without errors"""
    # Test core dependencies
    import streamlit
    import chromadb
    import fitz  # PyMuPDF
    import google.generativeai
    import pandas as pd
    import numpy as np
    
    # Test our modules
    from agents.pdf_parser import PDFParserAgent
    from agents.rag_agent import RAGAgent
    from agents.summarizer import SummarizerAgent
    from utils.database import PaperDatabase
    
    assert True  # If we get here, all imports worked

def test_pdf_parser_initialization():
    """Test PDF parser initialization"""
    from agents.pdf_parser import PDFParserAgent
    parser = PDFParserAgent()
    assert parser is not None
    assert hasattr(parser, 'process_paper')

def test_database_initialization():
    """Test database initialization"""
    from utils.database import PaperDatabase
    db = PaperDatabase()
    assert db is not None
    assert hasattr(db, 'add_paper')

def test_rag_agent_initialization():
    """Test RAG agent initialization"""
    from agents.rag_agent import RAGAgent
    rag = RAGAgent()
    assert rag is not None
    assert hasattr(rag, 'search_papers')

@pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="Gemini API key not set")
def test_summarizer_initialization():
    """Test summarizer initialization (only if API key is set)"""
    from agents.summarizer import SummarizerAgent
    try:
        summarizer = SummarizerAgent()
        assert summarizer is not None
    except Exception as e:
        # If initialization fails due to API key, that's OK for tests
        if "API key" in str(e):
            pytest.skip("Gemini API key invalid or not set")
        else:
            raise e

def test_environment_variables():
    """Test that environment can be loaded"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # This should not raise an error
    assert True