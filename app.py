import streamlit as st
import os
import tempfile
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px

from agents.pdf_parser import PDFParserAgent
from agents.rag_agent import RAGAgent
from agents.summarizer import SummarizerAgent
from utils.database import PaperDatabase

class ResearchAssistantApp:
    def __init__(self):
        self.pdf_parser = PDFParserAgent()
        self.rag_agent = RAGAgent()
        self.summarizer = SummarizerAgent()
        self.paper_db = PaperDatabase()
        
        # Initialize session state
        if 'processed_papers' not in st.session_state:
            st.session_state.processed_papers = []
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'current_analysis' not in st.session_state:
            st.session_state.current_analysis = None
    
    def run(self):
        st.set_page_config(
            page_title="AI Research Assistant",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🤖 AI Research Assistant for Papers & PDFs")
        st.markdown("""
        Upload your research papers and get instant insights, summaries, and comparative analysis.
        Perfect for researchers overwhelmed by the exponential growth in published papers.
        """)
        
        # Sidebar
        st.sidebar.title("Navigation")
        app_mode = st.sidebar.selectbox(
            "Choose Mode",
            ["Upload Papers", "Search & Analyze", "Comparative Analysis", "Impact Metrics"]
        )
        
        if app_mode == "Upload Papers":
            self.upload_papers_section()
        elif app_mode == "Search & Analyze":
            self.search_analyze_section()
        elif app_mode == "Comparative Analysis":
            self.comparative_analysis_section()
        elif app_mode == "Impact Metrics":
            self.impact_metrics_section()
    
    def upload_papers_section(self):
        st.header("📤 Upload Research Papers")
        
        uploaded_files = st.file_uploader(
            "Upload PDF papers",
            type="pdf",
            accept_multiple_files=True,
            help="Upload multiple PDF research papers"
        )
        
        if uploaded_files:
            if st.button("Process Papers"):
                with st.spinner("Processing papers..."):
                    self.process_uploaded_files(uploaded_files)
    
    def process_uploaded_files(self, uploaded_files):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processed_papers = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Process PDF
            paper_metadata = self.pdf_parser.process_paper(tmp_path)
            
            if paper_metadata:
                # Ensure all fields have proper values
                paper_data = {
                    'title': paper_metadata.title or "Unknown Title",
                    'authors': paper_metadata.authors or [],
                    'abstract': paper_metadata.abstract or "",
                    'citations': paper_metadata.citations or [],
                    'year': paper_metadata.year,  # Can be None
                    'journal': paper_metadata.journal or "",
                    'keywords': paper_metadata.keywords or [],
                    'full_text': paper_metadata.full_text or "",
                    'file_path': uploaded_file.name
                }
                
                paper_id = self.paper_db.add_paper(paper_data)
                paper_data['id'] = paper_id
                paper_data['citation_count'] = len(paper_data['citations'])  # Add citation_count for RAG
                
                processed_papers.append(paper_data)
                
                # Clean up temp file
                os.unlink(tmp_path)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Update RAG agent with new papers
        if processed_papers:
            try:
                self.rag_agent.add_papers(processed_papers)
                st.session_state.processed_papers.extend(processed_papers)
                
                st.success(f"✅ Successfully processed {len(processed_papers)} papers!")
                
                # Show summary
                st.subheader("Processing Summary")
                summary_data = []
                for paper in processed_papers:
                    summary_data.append({
                        'Title': paper['title'],
                        'Authors': ', '.join(paper['authors'][:3]) + ('...' if len(paper['authors']) > 3 else ''),
                        'Year': paper.get('year', 'N/A') or 'N/A',
                        'Citations Found': len(paper['citations']),
                        'Keywords': ', '.join(paper['keywords'][:3]) if paper['keywords'] else 'N/A'
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error adding papers to search database: {e}")
                st.info("Papers were saved but may not be searchable. Please try uploading again.")
    
    def search_analyze_section(self):
        st.header("🔍 Search & Analyze Papers")
        
        if not st.session_state.processed_papers:
            st.warning("Please upload some papers first in the 'Upload Papers' section.")
            return
        
        # Search interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input(
                "Search query",
                placeholder="e.g., contrastive learning medical imaging transformer architectures"
            )
        
        with col2:
            n_results = st.number_input("Number of results", min_value=1, max_value=50, value=10)
        
        specific_topics = st.multiselect(
            "Specific topics to extract",
            ['architectures', 'datasets', 'evaluation methods', 'results', 'limitations', 'contributions'],
            default=['architectures', 'datasets', 'evaluation methods', 'results']
        )
        
        if st.button("Search Papers") and query:
            try:
                with st.spinner("Searching for relevant papers..."):
                    search_results = self.rag_agent.search_papers(query, n_results)
                    
                    # Enhance search results with database IDs
                    enhanced_results = []
                    for result in search_results:
                        # Try to find the paper in our database
                        matching_paper = None
                        for db_paper in st.session_state.processed_papers:
                            if (db_paper.get('title', '').lower() in result.get('title', '').lower() or 
                                result.get('title', '').lower() in db_paper.get('title', '').lower()):
                                matching_paper = db_paper
                                break
                        
                        if matching_paper:
                            result['db_id'] = matching_paper['id']
                            result['has_full_text'] = bool(matching_paper.get('full_text'))
                        else:
                            result['db_id'] = None
                            result['has_full_text'] = False
                        
                        enhanced_results.append(result)
                    
                    ranked_results = self.rag_agent.rank_papers_by_relevance(enhanced_results, query)
                    st.session_state.search_results = ranked_results
                    
                    # Clear previous analysis when new search is performed
                    st.session_state.current_analysis = None
                    
            except Exception as e:
                st.error(f"Search failed: {e}")
        
        # Display search results if they exist
        if st.session_state.search_results:
            self.display_search_results(st.session_state.search_results, specific_topics)
    
    def display_search_results(self, results: List[Dict], topics: List[str]):
        st.subheader(f"📊 Top {len(results)} Relevant Papers")
        
        if not results:
            st.info("No results found. Try a different search query.")
            return
        
        # Show search statistics
        unique_scores = len(set(paper.get('relevance_score', 0) for paper in results))
        st.info(f"Showing {len(results)} unique papers with {unique_scores} different relevance scores")
            
        for i, paper in enumerate(results, 1):
            # Create expander without key parameter
            with st.expander(f"#{i} {paper.get('title', 'Unknown Title')} (Score: {paper.get('relevance_score', 0):.3f})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Authors:** {paper.get('authors', 'Unknown Authors')}")
                    st.write(f"**Year:** {paper.get('year', 'N/A')}")
                    st.write(f"**Journal:** {paper.get('journal', 'N/A')}")
                    st.write(f"**Citations:** {paper.get('citation_count', 'N/A')}")
                    
                    # Show abstract with better formatting
                    abstract = paper.get('abstract', 'No abstract available')
                    st.write(f"**Abstract:** {abstract[:500]}{'...' if len(abstract) > 500 else ''}")
                    
                    # Show analysis status
                    if paper.get('db_id'):
                        st.success("✅ Paper available for detailed analysis")
                    else:
                        st.warning("⚠️ Paper not found in database - limited analysis available")
                
                with col2:
                    # Create a unique button key
                    button_key = f"analyze_btn_{i}"
                    
                    # Check if this paper is currently being analyzed - ensure boolean
                    is_current_analysis = False
                    if (st.session_state.current_analysis and 
                        st.session_state.current_analysis.get('paper_index') == i):
                        is_current_analysis = True
                    
                    # Ensure disabled parameter is always boolean
                    if st.button(f"🔍 Analyze Topics", key=button_key, type="secondary", disabled=bool(is_current_analysis)):
                        # Set current analysis state
                        st.session_state.current_analysis = {
                            'paper_index': i,
                            'paper_data': paper,
                            'topics': topics,
                            'status': 'processing'
                        }
                        
                        # Rerun to trigger the analysis
                        st.rerun()
                
                # Display analysis results if this paper is being analyzed
                if (st.session_state.current_analysis and 
                    st.session_state.current_analysis.get('paper_index') == i):
                    
                    analysis_data = st.session_state.current_analysis
                    
                    if analysis_data.get('status') == 'processing':
                        with st.spinner("🤖 Extracting key topics with Gemini AI..."):
                            try:
                                analysis_text = ""
                                paper_source = ""
                                
                                # Try to get full text from database if available
                                if paper.get('db_id'):
                                    db_paper = self.paper_db.get_paper(paper['db_id'])
                                    if db_paper and db_paper.get('full_text'):
                                        analysis_text = db_paper['full_text']
                                        paper_source = "database full text"
                                    elif db_paper and db_paper.get('abstract'):
                                        analysis_text = db_paper['abstract']
                                        paper_source = "database abstract"
                                
                                # Fallback to search result abstract
                                if not analysis_text and paper.get('abstract'):
                                    analysis_text = paper['abstract']
                                    paper_source = "search result abstract"
                                
                                if analysis_text:
                                    st.info(f"📖 Analyzing {paper_source} ({len(analysis_text)} characters)")
                                    
                                    # Extract topics using Gemini
                                    topics_summary = self.summarizer.extract_key_topics(analysis_text, topics)
                                    
                                    # Update session state with results
                                    st.session_state.current_analysis = {
                                        'paper_index': i,
                                        'paper_data': paper,
                                        'topics': topics,
                                        'status': 'completed',
                                        'results': topics_summary,
                                        'paper_source': paper_source,
                                        'text_length': len(analysis_text)
                                    }
                                    
                                    # Rerun to display results
                                    st.rerun()
                                    
                                else:
                                    st.session_state.current_analysis = {
                                        'paper_index': i,
                                        'paper_data': paper,
                                        'topics': topics,
                                        'status': 'error',
                                        'error': "No text content available for analysis. Please try reprocessing the PDF."
                                    }
                                    st.rerun()
                                    
                            except Exception as e:
                                st.session_state.current_analysis = {
                                    'paper_index': i,
                                    'paper_data': paper,
                                    'topics': topics,
                                    'status': 'error',
                                    'error': f"Topic extraction failed: {str(e)}"
                                }
                                st.rerun()
                    
                    elif analysis_data.get('status') == 'completed':
                        st.success("✅ Analysis completed!")
                        
                        # Display the analysis results
                        st.subheader("🎯 AI-Powered Topic Analysis")
                        
                        results_data = analysis_data.get('results', {})
                        for topic, content in results_data.items():
                            st.write(f"**{topic.upper().replace('_', ' ')}:**")
                            if content and content not in ["Not specified", "Analysis failed"]:
                                # Format content with better presentation
                                lines = content.split('. ')
                                for line in lines:
                                    if line.strip():
                                        st.write(f"• {line.strip()}")
                            else:
                                st.info("No specific information found for this topic.")
                            st.write("---")
                        
                        # Add a button to clear analysis
                        if st.button("🔄 Clear Analysis", key=f"clear_{i}"):
                            st.session_state.current_analysis = None
                            st.rerun()
                    
                    elif analysis_data.get('status') == 'error':
                        st.error(analysis_data.get('error', 'Unknown error occurred'))
                        st.info("This might be due to:")
                        st.write("- Gemini API quota limits")
                        st.write("- Network connection issues") 
                        st.write("- Insufficient text content")
                        
                        # Add a button to retry
                        if st.button("🔄 Retry Analysis", key=f"retry_{i}"):
                            st.session_state.current_analysis = None
                            st.rerun()
    
    def comparative_analysis_section(self):
        st.header("📈 Comparative Analysis")
        
        if not st.session_state.processed_papers:
            st.warning("Please upload some papers first.")
            return
        
        # Paper selection for comparison
        paper_options = {paper.get('title', 'Unknown Title'): paper for paper in st.session_state.processed_papers}
        selected_titles = st.multiselect(
            "Select papers for comparison",
            list(paper_options.keys()),
            default=list(paper_options.keys())[:3] if len(paper_options) >= 3 else list(paper_options.keys())
        )
        
        selected_papers = [paper_options[title] for title in selected_titles if title in paper_options]
        
        if st.button("Generate Comparative Analysis") and selected_papers:
            with st.spinner("Generating comparative analysis..."):
                try:
                    analysis = self.summarizer.generate_comparative_analysis(selected_papers)
                    
                    st.subheader("Comparative Research Map")
                    st.write(analysis)
                    
                    # Create comparison table
                    st.subheader("Key Topics Comparison")
                    comparison_data = []
                    
                    for paper in selected_papers:
                        try:
                            topics = self.summarizer.extract_key_topics(
                                paper.get('full_text', paper.get('abstract', '')),
                                ['architectures', 'datasets', 'evaluation methods']
                            )
                            
                            comparison_data.append({
                                'Title': paper.get('title', 'Unknown Title'),
                                'Architectures': topics.get('architectures', 'N/A')[:100] + '...',
                                'Datasets': topics.get('datasets', 'N/A')[:100] + '...',
                                'Evaluation Methods': topics.get('evaluation methods', 'N/A')[:100] + '...',
                                'Year': paper.get('year', 'N/A') or 'N/A',
                                'Citations': len(paper.get('citations', []))
                            })
                        except Exception as e:
                            st.error(f"Error analyzing paper {paper.get('title', 'Unknown')}: {e}")
                    
                    if comparison_data:
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(comparison_df, use_container_width=True)
                    else:
                        st.warning("Could not generate comparison table.")
                        
                except Exception as e:
                    st.error(f"Comparative analysis failed: {e}")
    
    def impact_metrics_section(self):
        st.header("📊 Research Impact Metrics")
        
        if not st.session_state.processed_papers:
            st.warning("Please upload some papers first.")
            return
        
        # Calculate impact metrics with error handling
        try:
            metrics = self.summarizer.calculate_impact_metrics(st.session_state.processed_papers)
        except Exception as e:
            st.error(f"Error calculating metrics: {e}")
            # Create default metrics to prevent crash
            metrics = {
                'h_index': 0,
                'i10_index': 0,
                'average_citations': 0,
                'total_citations': 0,
                'journal_tiers': {},
                'paper_count': len(st.session_state.processed_papers)
            }
        
        # Display metrics with safe defaults
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Papers", metrics.get('paper_count', 0))
        with col2:
            st.metric("h-index", metrics.get('h_index', 0))
        with col3:
            st.metric("i10-index", metrics.get('i10_index', 0))
        with col4:
            st.metric("Avg Citations", f"{metrics.get('average_citations', 0):.1f}")
        
        # Visualization with safe data
        try:
            st.subheader("📈 Citation Distribution")
            citation_counts = [paper.get('citation_count', 0) or 0 for paper in st.session_state.processed_papers]
            
            if citation_counts and any(citation_counts):
                fig = px.histogram(
                    x=citation_counts,
                    nbins=20,
                    title="Distribution of Citation Counts",
                    labels={'x': 'Citation Count', 'y': 'Number of Papers'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No citation data available for visualization")
        except Exception as e:
            st.error(f"Error creating citation visualization: {e}")
        
        # Journal tiers with safe data
        try:
            st.subheader("Journal Tier Distribution")
            journal_tiers = metrics.get('journal_tiers', {})
            tier_counts = {}
            for tier in journal_tiers.values():
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            if tier_counts:
                fig_pie = px.pie(
                    values=list(tier_counts.values()),
                    names=list(tier_counts.keys()),
                    title="Journal Tier Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No journal tier data available")
        except Exception as e:
            st.error(f"Error creating journal tier visualization: {e}")
        
        # Paper impact table with safe data - UPDATED SECTION
        try:
            st.subheader("📋 Paper Impact Ranking")
            
            # Calculate individual paper metrics
            impact_data = []
            for paper in st.session_state.processed_papers:
                # Get paper-specific metrics
                paper_citations = paper.get('citation_count', 0) or 0
                paper_year = paper.get('year', 'N/A')
                
                # Format year properly
                if paper_year and str(paper_year).isdigit():
                    paper_year = int(paper_year)
                else:
                    paper_year = 'N/A'
                
                # Calculate individual paper's contribution to h-index and i10-index
                # For h-index: count how many papers have at least this paper's citation count
                papers_with_more_citations = sum(1 for p in st.session_state.processed_papers 
                                               if (p.get('citation_count', 0) or 0) >= paper_citations)
                
                # For i10-index: check if this paper has 10+ citations
                contributes_to_i10 = 1 if paper_citations >= 10 else 0
                
                impact_data.append({
                    'Title': paper.get('title', 'Unknown Title'),
                    'Citations': paper_citations,
                    'Year': paper_year,
                    'Journal Tier': metrics.get('journal_tiers', {}).get(paper.get('title', ''), 'N/A'),
                    'Authors': ', '.join(paper.get('authors', [])[:2]) + ('...' if len(paper.get('authors', [])) > 2 else ''),
                    'Contributes to h-index': f"{papers_with_more_citations}+ citations",
                    'Contributes to i10-index': 'Yes' if contributes_to_i10 else 'No'
                })
            
            impact_df = pd.DataFrame(impact_data)
            impact_df = impact_df.sort_values('Citations', ascending=False)
            
            # Display the table
            st.dataframe(impact_df, use_container_width=True)
            
            # Add explanation
            with st.expander("ℹ️ How these metrics are calculated"):
                st.markdown("""
                **Metrics Explanation:**
                - **Citations**: Number of citations found in the paper
                - **Contributes to h-index**: Shows how many papers have at least this many citations
                - **Contributes to i10-index**: Whether this paper has 10 or more citations
                - **Journal Tier**: Quality ranking based on journal reputation
                
                **Collection-wide Metrics:**
                - **h-index**: {h} papers with at least {h} citations each
                - **i10-index**: {i10} papers with at least 10 citations each
                - **Total Citations**: {total} across all papers
                """.format(
                    h=metrics.get('h_index', 0),
                    i10=metrics.get('i10_index', 0),
                    total=metrics.get('total_citations', 0)
                ))
                
        except Exception as e:
            st.error(f"Error creating impact table: {e}")

def main():
    app = ResearchAssistantApp()
    app.run()

if __name__ == "__main__":
    main()