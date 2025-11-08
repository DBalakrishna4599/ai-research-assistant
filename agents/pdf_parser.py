import fitz  # PyMuPDF
import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PaperMetadata:
    title: str
    authors: List[str]
    abstract: str
    citations: List[str]
    year: Optional[int]
    journal: str
    keywords: List[str]
    full_text: str

class PDFParserAgent:
    def __init__(self):
        self.citation_patterns = [
            r'\[(\d+)\]',  # [1], [2-5]
            r'\(([^)]+?\d{4}[^)]*?)\)',  # (Author et al., 2020)
        ]
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def extract_metadata(self, text: str) -> PaperMetadata:
        """Extract metadata from paper text with proper defaults"""
        # Extract title (usually first few lines)
        lines = text.split('\n')
        title = self._extract_title(lines) or "Unknown Title"
        authors = self._extract_authors(text) or []
        abstract = self._extract_abstract(text) or ""
        citations = self._extract_citations(text) or []
        year = self._extract_year(text)  # Can be None
        journal = self._extract_journal(text) or ""
        keywords = self._extract_keywords(text) or []
        
        return PaperMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
            citations=citations,
            year=year,
            journal=journal,
            keywords=keywords,
            full_text=text
        )
    
    def _extract_title(self, lines: List[str]) -> str:
        """Extract paper title"""
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if (len(line) > 20 and len(line) < 200 and 
                not line.lower().startswith('abstract') and
                not line.lower().startswith('keywords') and
                not line.isupper()):
                return line
        return "Unknown Title"
    
    def _extract_authors(self, text: str) -> List[str]:
        """Extract authors"""
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):
            if any(keyword in line.lower() for keyword in ['university', 'institute', 'college', '@']):
                # Look backwards for authors
                author_lines = []
                for j in range(max(0, i-3), i):
                    if lines[j].strip() and len(lines[j].strip()) > 3:
                        author_lines.append(lines[j].strip())
                if author_lines:
                    return self._parse_authors(' '.join(author_lines))
        return []
    
    def _parse_authors(self, author_text: str) -> List[str]:
        """Parse author names from text"""
        # Simple parsing - split by commas and "and"
        authors = re.split(r',|\band\b', author_text)
        return [author.strip() for author in authors if author.strip()]
    
    def _extract_abstract(self, text: str) -> str:
        """Extract abstract section"""
        abstract_patterns = [
            r'abstract\s*\n(.*?)(?=\n\s*\d|\n\s*introduction|\n\s*keywords|\n\s*1\.)',
            r'ABSTRACT\s*\n(.*?)(?=\n\s*\d|\n\s*INTRODUCTION|\n\s*KEYWORDS|\n\s*1\.)'
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:1000]  # Limit length
        
        return ""
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract cited references"""
        citations = set()
        
        # Extract citation markers
        for pattern in self.citation_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    citations.update(match)
                else:
                    citations.add(match)
        
        return list(citations)
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract publication year"""
        year_pattern = r'\b(19|20)\d{2}\b'
        matches = re.findall(year_pattern, text)
        if matches:
            return int(matches[0])
        return None
    
    def _extract_journal(self, text: str) -> str:
        """Extract journal/conference name"""
        # Look for common journal patterns in first few lines
        lines = text.split('\n')[:50]
        for line in lines:
            line_lower = line.lower()
            if any(journal in line_lower for journal in ['proceedings', 'journal', 'conference', 'arxiv']):
                return line.strip()
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords"""
        keyword_patterns = [
            r'keywords:\s*(.*?)(?=\n\s*\w)',
            r'key words:\s*(.*?)(?=\n\s*\w)',
            r'index terms:\s*(.*?)(?=\n\s*\w)'
        ]
        
        for pattern in keyword_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                keywords_text = match.group(1)
                # Split by commas, semicolons, etc.
                keywords = re.split(r'[;,•]', keywords_text)
                return [kw.strip() for kw in keywords if kw.strip()]
        
        return []
    
    def process_paper(self, pdf_path: str) -> Optional[PaperMetadata]:
        """Process a single PDF paper"""
        text = self.extract_text(pdf_path)
        if not text:
            return None
        
        return self.extract_metadata(text)