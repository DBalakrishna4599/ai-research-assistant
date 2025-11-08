import google.generativeai as genai
import os
from typing import Dict, List, Any
import re
from dotenv import load_dotenv
import time

load_dotenv()

class SummarizerAgent:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            raise ValueError("❌ Please add your Gemini API key to the .env file")
        
        print(f"🔑 Gemini API Key loaded: {api_key[:10]}...{api_key[-10:]}")
        
        try:
            genai.configure(api_key=api_key)
            
            # Use gemini-1.5-flash for better quota usage
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Gemini 2.0 Flash model initialized successfully")
            
        except Exception as e:
            print(f"❌ Gemini initialization failed: {e}")
            raise
    
    def extract_key_topics(self, paper_text: str, specific_topics: List[str] = None) -> Dict[str, Any]:
        """Extract key topics from paper using Gemini AI"""
        if specific_topics is None:
            specific_topics = ['architectures', 'datasets', 'evaluation methods', 'results']
        
        # Check if we have text to analyze
        if not paper_text or len(paper_text.strip()) < 50:
            return {topic: "Insufficient text for analysis" for topic in specific_topics}
        
        # Smart text processing for optimal token usage
        processed_text = self._prepare_paper_text(paper_text)
        
        print(f"🔍 Analyzing text of length: {len(processed_text)} characters")
        print(f"🎯 Topics to extract: {specific_topics}")
        
        prompt = f"""
        RESEARCH PAPER ANALYSIS TASK:
        
        Analyze this academic paper and extract specific information in a structured format.
        
        PAPER CONTENT:
        {processed_text}
        
        EXTRACT THE FOLLOWING INFORMATION:
        {chr(10).join([f"• {topic.upper()}: " for topic in specific_topics])}
        
        RESPONSE FORMAT REQUIREMENTS:
        - Use exactly this format for each topic: TOPIC_NAME: content
        - Be specific and factual
        - Use bullet points or short phrases
        - If information is missing, write "Not specified"
        - Focus on concrete details from the paper
        
        IMPORTANT: Start each topic on a new line with the exact topic name in uppercase followed by colon.
        """
        
        try:
            # Add small delay to avoid rate limits
            time.sleep(2)
            
            print("🤖 Calling Gemini API...")
            response = self.model.generate_content(prompt)
            print("✅ Gemini analysis completed successfully")
            
            # Debug: Print raw response
            print(f"📄 Raw response length: {len(response.text)}")
            
            parsed_response = self._parse_summary_response(response.text, specific_topics)
            print(f"📊 Parsed {len(parsed_response)} topics")
            
            return parsed_response
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            error_msg = f"Analysis failed: {str(e)}"
            
            # Provide more specific error messages
            if "quota" in str(e).lower():
                error_msg = "Gemini API quota exceeded. Please check your usage or try again later."
            elif "API_KEY" in str(e):
                error_msg = "Invalid Gemini API key. Please check your .env file."
            elif "connect" in str(e).lower():
                error_msg = "Network connection error. Please check your internet connection."
                
            return {topic: error_msg for topic in specific_topics}
    
    def _prepare_paper_text(self, text: str, max_length: int = 8000) -> str:
        """Prepare paper text for analysis by extracting key sections"""
        if not text:
            return "No text content available"
            
        if len(text) <= max_length:
            return text
        
        # Extract key sections in order of importance
        sections = []
        
        # 1. Abstract (most important)
        abstract_match = re.search(r'abstract(.*?)(?=introduction|$)', text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            sections.append("ABSTRACT: " + abstract_match.group(1).strip()[:1500])
        
        # 2. Introduction
        intro_match = re.search(r'introduction(.*?)(?=method|background|related|$)', text, re.IGNORECASE | re.DOTALL)
        if intro_match:
            sections.append("INTRODUCTION: " + intro_match.group(1).strip()[:1500])
        
        # 3. Methodology
        method_match = re.search(r'method(.*?)(?=experiment|result|evaluation|$)', text, re.IGNORECASE | re.DOTALL)
        if method_match:
            sections.append("METHODOLOGY: " + method_match.group(1).strip()[:1500])
        
        # 4. Results
        results_match = re.search(r'result(.*?)(?=conclusion|discussion|$)', text, re.IGNORECASE | re.DOTALL)
        if results_match:
            sections.append("RESULTS: " + results_match.group(1).strip()[:1500])
        
        # If we couldn't extract sections, use beginning of text
        if not sections:
            return text[:max_length]
        
        return "\n\n".join(sections)
    
    def _parse_summary_response(self, response_text: str, topics: List[str]) -> Dict[str, Any]:
        """Parse the Gemini response into structured data"""
        summary = {}
        
        for topic in topics:
            # Try multiple pattern formats
            patterns = [
                f"{topic.upper()}:(.*?)(?=\\n[A-Z][A-Z_\\s]+:|\\n*$)",
                f"{topic.upper()}S:(.*?)(?=\\n[A-Z][A-Z_\\s]+:|\\n*$)",
                f"{topic.replace(' ', '_').upper()}:(.*?)(?=\\n[A-Z][A-Z_\\s]+:|\\n*$)",
            ]
            
            content_found = False
            for pattern in patterns:
                match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                if match:
                    content = match.group(1).strip()
                    # Clean up content
                    content = re.sub(r'^[-•*]\s*', '', content, flags=re.MULTILINE)
                    content = re.sub(r'\s+', ' ', content).strip()
                    summary[topic.lower()] = content
                    content_found = True
                    break
            
            if not content_found:
                summary[topic.lower()] = "Not specified"
        
        return summary
    
    def generate_comparative_analysis(self, papers: List[Dict]) -> str:
        """Generate comparative analysis of multiple papers"""
        if not papers:
            return "No papers available for comparison"
            
        if len(papers) > 4:
            papers = papers[:4]  # Limit to avoid token limits
        
        paper_info = []
        for i, paper in enumerate(papers):
            paper_info.append({
                'number': i + 1,
                'title': paper.get('title', 'Unknown Title'),
                'authors': ', '.join(paper.get('authors', [])[:3]) if paper.get('authors') else 'Unknown Authors',
                'year': paper.get('year', 'Unknown') or 'Unknown',
                'abstract': (paper.get('abstract', '')[:300] + '...') if len(paper.get('abstract', '')) > 300 else (paper.get('abstract', '') or 'No abstract')
            })
        
        prompt = f"""
        COMPARATIVE RESEARCH ANALYSIS:
        
        Compare these research papers and provide insights:
        
        PAPERS:
        {chr(10).join([f"{p['number']}. {p['title']} ({p['year']}) - Authors: {p['authors']}" for p in paper_info])}
        
        ABSTRACT SUMMARIES:
        {chr(10).join([f"Paper {p['number']}: {p['abstract']}" for p in paper_info])}
        
        ANALYSIS REQUEST:
        Please provide a comprehensive comparison covering:
        
        1. COMMONALITIES: Shared methodologies, techniques, or approaches
        2. DIFFERENCES: Contrasting methods, objectives, or findings  
        3. DATASETS & EVALUATION: Comparison of data sources and evaluation methods
        4. INNOVATIONS: Unique contributions of each paper
        5. RESEARCH GAPS: Opportunities for future work
        6. SYNTHESIS: Overall assessment of the research landscape
        
        Format your response with clear headings and bullet points for readability.
        """
        
        try:
            time.sleep(2)  # Rate limiting
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Comparative analysis failed: {str(e)}"
    
    def calculate_impact_metrics(self, papers: List[Dict]) -> Dict[str, Any]:
        """Calculate impact metrics for papers with proper year handling"""
        if not papers:
            return {
                'h_index': 0,
                'i10_index': 0,
                'average_citations': 0,
                'total_citations': 0,
                'journal_tiers': {},
                'paper_count': 0
            }
        
        citation_counts = [paper.get('citation_count', 0) or 0 for paper in papers]
        
        # Calculate h-index
        sorted_citations = sorted(citation_counts, reverse=True)
        h_index = 0
        for i, citations in enumerate(sorted_citations):
            if citations >= i + 1:
                h_index = i + 1
            else:
                break
        
        # Calculate i10-index
        i10_index = sum(1 for citations in citation_counts if citations >= 10)
        
        # Journal tier classification with proper null checking
        journal_tiers = {}
        for paper in papers:
            journal = paper.get('journal', '') or ''
            journal_lower = journal.lower() if journal else ''
            paper_title = paper.get('title', 'Unknown Title') or 'Unknown Title'
            
            if any(q1 in journal_lower for q1 in ['nature', 'science', 'cell', 'proceedings of the national academy of sciences']):
                journal_tiers[paper_title] = 'Q1'
            elif any(q2 in journal_lower for q2 in ['ieee', 'acm', 'springer', 'elsevier']):
                journal_tiers[paper_title] = 'Q2'
            elif any(q3 in journal_lower for q3 in ['arxiv', 'workshop', 'conference']):
                journal_tiers[paper_title] = 'Q3'
            else:
                journal_tiers[paper_title] = 'Q4/Other'
        
        return {
            'h_index': h_index,
            'i10_index': i10_index,
            'average_citations': sum(citation_counts) / len(citation_counts) if citation_counts else 0,
            'total_citations': sum(citation_counts),
            'journal_tiers': journal_tiers,
            'paper_count': len(papers)
        }