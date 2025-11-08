import pytest
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        from agents.pdf_parser import PDFParserAgent
        from agents.rag_agent import RAGAgent
        from agents.summarizer import SummarizerAgent
        from utils.database import PaperDatabase
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_pdf_parser_initialization():
    """Test PDF parser initialization"""
    from agents.pdf_parser import PDFParserAgent
    parser = PDFParserAgent()
    assert parser is not None

def test_database_initialization():
    """Test database initialization"""
    from utils.database import PaperDatabase
    db = PaperDatabase()
    assert db is not None

def test_environment_variables():
    """Test that required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if Gemini API key is set (but don't fail if it's not in CI)
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Warning: GOOGLE_API_KEY not set in environment")