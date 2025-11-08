from agents.rag_agent import RAGAgent
from utils.database import PaperDatabase
import os

def reset_database():
    print("🔄 Resetting database...")
    
    # Clear ChromaDB
    rag = RAGAgent()
    if rag.clear_database():
        print("✅ ChromaDB cleared successfully")
    else:
        print("❌ Failed to clear ChromaDB")
    
    # Delete SQLite database
    if os.path.exists("research_papers.db"):
        os.remove("research_papers.db")
        print("✅ SQLite database deleted")
    
    # Reinitialize database
    db = PaperDatabase()
    print("✅ Database reinitialized")
    
    print("\n🎉 Database reset complete!")
    print("Now re-upload your papers to get clean search results.")

if __name__ == "__main__":
    reset_database()