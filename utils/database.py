import sqlite3
import json
from typing import List, Dict, Any, Optional

class PaperDatabase:
    def __init__(self, db_path: str = "research_papers.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                authors TEXT,
                abstract TEXT,
                citations TEXT,
                year INTEGER,
                journal TEXT,
                keywords TEXT,
                full_text TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_paper(self, paper_data: Dict[str, Any]) -> int:
        """Add a paper to the database with proper data validation"""
        # Ensure all fields have proper values
        validated_data = {
            'title': paper_data.get('title', 'Unknown Title') or 'Unknown Title',
            'authors': paper_data.get('authors', []) or [],
            'abstract': paper_data.get('abstract', '') or '',
            'citations': paper_data.get('citations', []) or [],
            'year': paper_data.get('year'),  # Can be None
            'journal': paper_data.get('journal', '') or '',
            'keywords': paper_data.get('keywords', []) or [],
            'full_text': paper_data.get('full_text', '') or '',
            'file_path': paper_data.get('file_path', '') or ''
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO papers (title, authors, abstract, citations, year, journal, keywords, full_text, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            validated_data['title'],
            json.dumps(validated_data['authors']),
            validated_data['abstract'],
            json.dumps(validated_data['citations']),
            validated_data['year'],
            validated_data['journal'],
            json.dumps(validated_data['keywords']),
            validated_data['full_text'],
            validated_data['file_path']
        ))
        
        paper_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return paper_id
    
    def get_paper(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """Get paper by ID with proper data handling"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1] or "Unknown Title",
                'authors': json.loads(row[2]) if row[2] else [],
                'abstract': row[3] or "",
                'citations': json.loads(row[4]) if row[4] else [],
                'year': row[5],  # Can be None
                'journal': row[6] or "",
                'keywords': json.loads(row[7]) if row[7] else [],
                'full_text': row[8] or "",
                'file_path': row[9] or ""
            }
        return None
    
    def get_all_papers(self) -> List[Dict[str, Any]]:
        """Get all papers from database with proper data handling"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM papers')
        rows = cursor.fetchall()
        conn.close()
        
        papers = []
        for row in rows:
            papers.append({
                'id': row[0],
                'title': row[1] or "Unknown Title",
                'authors': json.loads(row[2]) if row[2] else [],
                'abstract': row[3] or "",
                'citations': json.loads(row[4]) if row[4] else [],
                'year': row[5],
                'journal': row[6] or "",
                'keywords': json.loads(row[7]) if row[7] else [],
                'full_text': row[8] or "",
                'file_path': row[9] or ""
            })
        
        return papers
    
    def find_paper_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Find paper by title (fuzzy matching)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM papers WHERE title LIKE ?', (f'%{title}%',))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1] or "Unknown Title",
                'authors': json.loads(row[2]) if row[2] else [],
                'abstract': row[3] or "",
                'citations': json.loads(row[4]) if row[4] else [],
                'year': row[5],
                'journal': row[6] or "",
                'keywords': json.loads(row[7]) if row[7] else [],
                'full_text': row[8] or "",
                'file_path': row[9] or ""
            }
        return None
    
    def get_all_paper_titles(self) -> List[str]:
        """Get all paper titles from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT title FROM papers')
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows if row[0]]