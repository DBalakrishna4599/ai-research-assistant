AI Research Assistant 🤖📚
An intelligent agent that ingests a library of academic PDF papers, finds the most relevant documents based on a user's query, and provides AI-powered summaries, comparative analysis, and key research metrics.
This project helps researchers, students, and academics overcome the overwhelming volume of published literature by automating reading, synthesizing, and comparing findings.
🚀 Live Demo:
https://researchmindai-by-balakrishnachowdary-2300089049-klu.streamlit.app/
✨ Key Features
PDF Parsing: Extract full text, metadata (title, authors, journal), and citations from PDFs using PyMuPDF.
Semantic Search (RAG): Retrieval-Augmented Generation with sentence-transformers embeddings and ChromaDB for efficient vector storage and retrieval.
Intelligent Ranking: Improves search relevance considering title matches, citation counts, and publication year.
AI-Powered Analysis: Powered by Google Gemini API, providing:
Extraction of key topics (architectures, datasets, evaluation methods)
Comparative analysis across multiple papers
Calculation of research impact metrics (h-index, i10-index, journal tiers)
Interactive UI: User-friendly web interface built with Streamlit for easy paper upload, search, and analysis.
🛠️ Tech Stack
Layer	Technology
Frontend	Streamlit
Backend	Python
LLM	Google Gemini
Vector Database	ChromaDB
Embeddings	sentence-transformers (all-MiniLM-L6-v2)
PDF Parsing	PyMuPDF
CI/CD	GitHub Actions, Streamlit Community Cloud
📂 Project Structure
ai-research-assistant/
├── .github/
│   └── workflows/ci.yml
├── agents/
│   ├── __init__.py
│   ├── pdf_parser.py
│   ├── rag_agent.py
│   └── summarizer.py
├── data/sample_pdfs/
├── tests/test_app.py
├── utils/
│   ├── __init__.py
│   └── database.py
├── .env
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
⚙️ Local Setup & Installation
1. Clone the Repository
git clone https://github.com/DBalakrishna4599/ai-research-assistant.git
cd ai-research-assistant
2. Create & Activate a Virtual Environment
# Create environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Set Up Environment Variables
Create a .env file in the project root using the template .env.example and add your Gemini API key:
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
5. Run the Application
streamlit run app.py
Visit http://localhost:8501 in your browser.
📖 How to Use the App
Upload Papers: Navigate to the Upload Papers section to upload PDFs.
Search & Analyze: Go to Search & Analyze, enter a query to find relevant papers.
Get Insights: Click Analyze Topics to extract key information with the Gemini API.
Compare: Use Comparative Analysis and Impact Metrics for an overview of your research collection.
🤝 Contributing
Contributions, issues, and feature requests are welcome!
Fork the Project
Create your Feature Branch: git checkout -b feature/AmazingFeature
Commit your Changes: git commit -m "Add some AmazingFeature"
Push to the Branch: git push origin feature/AmazingFeature
Open a Pull Request
📝 License
Distributed under the MIT License. See LICENSE for more information.
🙏 Acknowledgments
Streamlit
Google Gemini
ChromaDB
Sentence Transformers
