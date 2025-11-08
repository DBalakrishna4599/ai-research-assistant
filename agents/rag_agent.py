import chromadb 
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os
import hashlib


class RAGAgent:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2',device='cpu')
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(
            name="research_papers",
            metadata={"description": "Research papers collection for semantic search"}
        )
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        return self.model.encode(text).tolist()
    
    def add_papers(self, papers: List[Dict[str, Any]]):
        """Add papers to the vector database with proper metadata handling"""
        documents = []
        metadatas = []
        ids = []
        
        for paper in papers:
            # Create document text for embedding
            title = paper.get('title', '') or ''
            abstract = paper.get('abstract', '') or ''
            keywords = paper.get('keywords', []) or []
            keywords_text = ' '.join(keywords) if keywords else ''
            
            doc_text = f"{title} {abstract} {keywords_text}"
            
            # Create unique ID based on paper content to avoid duplicates
            content_hash = hashlib.md5(doc_text.encode()).hexdigest()[:16]
            paper_id = f"{paper.get('id', '')}_{content_hash}"
            
            documents.append(doc_text)
            
            # Ensure all metadata fields have proper values (no None)
            metadata = {
                'title': title or "Unknown Title",
                'authors': ', '.join(paper.get('authors', [])) if paper.get('authors') else "Unknown Authors",
                'year': str(paper.get('year', '')) or "Unknown Year",
                'journal': paper.get('journal', '') or "Unknown Journal",
                'abstract': abstract or "No abstract",
                'citation_count': paper.get('citation_count', 0) or 0,
                'content_hash': content_hash  # Add hash for duplicate detection
            }
            
            metadatas.append(metadata)
            ids.append(paper_id)
        
        # Generate embeddings
        embeddings = [self.embed_text(doc) for doc in documents]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search_papers(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for relevant papers with duplicate removal"""
        query_embedding = self.embed_text(query)
        
        # Get more results to allow for duplicate filtering
        raw_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results * 3, 50),  # Get more results for filtering
            include=['metadatas', 'documents', 'distances']
        )
        
        formatted_results = []
        seen_titles = set()
        seen_hashes = set()
        
        if raw_results['metadatas'] and raw_results['metadatas'][0]:
            for i, metadata in enumerate(raw_results['metadatas'][0]):
                # Skip if no metadata
                if not metadata:
                    continue
                    
                title = metadata.get('title', 'Unknown Title')
                content_hash = metadata.get('content_hash', '')
                
                # Skip duplicates based on title similarity and content hash
                title_lower = title.lower().strip()
                is_duplicate = False
                
                # Check for exact duplicates
                if title_lower in seen_titles or content_hash in seen_hashes:
                    is_duplicate = True
                
                # Check for similar titles (fuzzy duplicate detection)
                for seen_title in seen_titles:
                    if (title_lower in seen_title or seen_title in title_lower) and len(title_lower) > 10:
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    continue
                
                # Add to seen sets
                seen_titles.add(title_lower)
                if content_hash:
                    seen_hashes.add(content_hash)
                
                # Calculate better relevance score
                base_score = 1 - raw_results['distances'][0][i] if raw_results['distances'] and raw_results['distances'][0] else 0.0
                
                # Enhance score with content-based features
                enhanced_score = self._enhance_relevance_score(metadata, query, base_score)
                
                formatted_results.append({
                    'title': title,
                    'authors': metadata.get('authors', 'Unknown Authors'),
                    'year': metadata.get('year', 'Unknown Year'),
                    'journal': metadata.get('journal', 'Unknown Journal'),
                    'abstract': metadata.get('abstract', 'No abstract'),
                    'citation_count': metadata.get('citation_count', 0),
                    'relevance_score': enhanced_score,
                    'content_hash': content_hash
                })
        
        # Sort by enhanced relevance score and return top n_results
        formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return formatted_results[:n_results]
    
    def _enhance_relevance_score(self, metadata: Dict, query: str, base_score: float) -> float:
        """Enhance relevance score with additional factors"""
        enhanced_score = base_score
        
        # Title relevance boost
        title = metadata.get('title', '').lower()
        query_terms = query.lower().split()
        
        # Boost if query terms appear in title
        title_boost = sum(1 for term in query_terms if term in title) * 0.1
        enhanced_score += min(title_boost, 0.3)
        
        # Citation count boost (normalized)
        citation_count = metadata.get('citation_count', 0)
        citation_boost = min(citation_count / 100.0, 0.2)
        enhanced_score += citation_boost
        
        # Recency boost
        year = metadata.get('year', '')
        if year and year.isdigit():
            year_int = int(year)
            if year_int >= 2020:
                enhanced_score += 0.1
            elif year_int >= 2015:
                enhanced_score += 0.05
        
        return min(enhanced_score, 1.0)
    
    def rank_papers_by_relevance(self, papers: List[Dict], query: str) -> List[Dict]:
        """Rank papers by relevance to query with enhanced scoring"""
        scored_papers = []
        
        for paper in papers:
            # Calculate enhanced relevance score
            score = self._calculate_enhanced_relevance_score(paper, query)
            paper['relevance_score'] = score
            scored_papers.append(paper)
        
        # Sort by relevance score
        return sorted(scored_papers, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _calculate_enhanced_relevance_score(self, paper: Dict, query: str) -> float:
        """Calculate comprehensive relevance score with enhanced features"""
        score = 0.0
        
        # Title relevance (highest weight) - with null safety
        title = paper.get('title', '') or ''
        title_lower = title.lower()
        query_lower = query.lower() if query else ''
        title_words = set(title_lower.split())
        query_words = set(query_lower.split())
        
        # Exact title matches get highest boost
        if query_lower in title_lower:
            score += 0.5
        elif title_words & query_words:
            score += 0.3
        
        # Abstract relevance - with null safety
        abstract = paper.get('abstract', '') or ''
        abstract_lower = abstract.lower()
        if query_words:  # Avoid division by zero
            abstract_match_ratio = len([w for w in query_words if w in abstract_lower]) / len(query_words)
            score += abstract_match_ratio * 0.2
        
        # Citation count influence (normalized) - with null safety
        citation_count = paper.get('citation_count', 0) or 0
        citation_score = min(citation_count / 100.0, 0.2)  # Cap at 0.2
        score += citation_score
        
        # Recency bonus (recent papers get small boost) - with null safety
        year = paper.get('year')
        if year and str(year).isdigit():
            year_int = int(year)
            if year_int >= 2020:
                score += 0.1
            elif year_int >= 2015:
                score += 0.05
        
        # Journal prestige bonus
        journal = paper.get('journal', '').lower()
        if any(prestigious in journal for prestigious in ['nature', 'science', 'cell', 'ieee', 'acm']):
            score += 0.05
        
        return min(score, 1.0)
    
    def clear_database(self):
        """Clear the entire database (use with caution)"""
        try:
            self.chroma_client.delete_collection("research_papers")
            self.collection = self.chroma_client.get_or_create_collection(
                name="research_papers",
                metadata={"description": "Research papers collection for semantic search"}
            )
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False