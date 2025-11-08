# 🤖 AI Research Assistant for Papers & PDFs

An intelligent research assistant that helps academics analyze, search, and compare research papers using AI-powered semantic search and topic extraction.

## 🚀 Features

- **PDF Parsing**: Extract text and metadata from research papers
- **Semantic Search**: Find relevant papers using RAG (Retrieval-Augmented Generation)
- **AI-Powered Analysis**: Extract key topics using Google Gemini AI
- **Comparative Analysis**: Compare multiple papers side-by-side
- **Impact Metrics**: Calculate h-index, i10-index, and journal rankings
- **Interactive UI**: Streamlit-based web interface

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DBalakrishna4599/research-assistant.git
   cd research-assistant

# Create requirements.txt (if not exists)
cat > requirements.txt << 'EOF'
streamlit==1.28.0
chromadb==0.4.15
pymupdf==1.23.7
python-dotenv==1.0.0
google-generativeai==0.3.0
numpy==1.24.0
pandas==2.0.0
scikit-learn==1.3.0
sentence-transformers==2.2.2
plotly==5.15.0
requests==2.31.0
tqdm==4.65.0
nltk==3.8.1
EOF



1. Create virtual environment:

   bash
    python -m venv research_env
      source research_env/bin/activate  # On Windows: research_env\Scripts\activate

2. Install dependencies:

    bash
      pip install -r requirements.txt

3. Set up environment variables:

    bash
    cp .env.example .env
      # Add your Gemini API key to .env

4. Run the application:

    bash
      streamlit run app.py


research-assistant/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # Project documentation
├── agents/               # AI agent modules
│   ├── pdf_parser.py    # PDF text extraction
│   ├── rag_agent.py     # Semantic search
│   └── summarizer.py    # AI topic extraction
├── utils/               # Utility modules
│   ├── database.py      # SQLite database operations
│   └── helpers.py       # Helper functions
└── data/               # Sample data and PDFs
    └── sample_pdfs/



🔧 Configuration
1.  Get Gemini API Key:

       Visit Google AI Studio
       Create an API key
       Add it to your .env file:

       text
          GOOGLE_API_KEY=your_gemini_api_key_here

2. Add Research Papers:

      Use the "Upload Papers" section in the app
          Or place PDFs in data/sample_pdfs/



🎯 Usage

1. Upload Papers: Process PDF research papers
2. Search & Analyze: Find relevant papers and extract key topics
3. Comparative Analysis: Compare multiple papers
4. Impact Metrics: View citation analysis and journal rankings




🐛 Troubleshooting

   Common Issues

      1. Gemini API Quota Exceeded:

        Check your usage at Google AI Studio
        Wait for daily reset or upgrade plan
    
      2. PDF Parsing Issues:

         Ensure PDFs are not password-protected
         Check that PyMuPDF is properly installed
         
      3. Database Errors:

        Run python reset_database.py to clear and reset


Getting Help: 

      Check the console for error messages
      Ensure all dependencies are installed
      Verify your API key is valid


🤝 Contributing

    Fork the repository
          Create a feature branch: git checkout -b feature/amazing-feature
          Commit changes: git commit -m 'Add amazing feature'
          Push to branch: git push origin feature/amazing-feature
          Open a Pull Request


📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

Streamlit for the web framework
Google Gemini AI for topic extraction
ChromaDB for vector search
Sentence Transformers for embeddings

### Create `.env.example`

```bash
# Google Gemini API Key
# Get your API key from: https://aistudio.google.com/
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0