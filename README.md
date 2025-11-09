An intelligent agent that ingests a library of academic PDF papers, finds the most relevant documents based on a user's query, and provides AI-powered summaries, comparative analysis, and key research metrics.

This project is designed to help researchers, students, and academics overcome the overwhelming volume of published literature by automating the process of reading, synthesizing, and comparing findings.

🚀 Live Demo
You can access and use the live application here:
https://researchmindai-by-balakrishnachowdary-2300089049-klu.streamlit.app/

✨ Key Features
PDF Parsing: Extracts full text, metadata (title, authors, journal), and citations from PDF files using PyMuPDF.

Semantic Search (RAG): Implements Retrieval-Augmented Generation using sentence-transformers for embeddings and ChromaDB for efficient vector storage and retrieval.

Intelligent Ranking: Enhances search relevance by considering title matches, citation counts, and publication year.

AI-Powered Analysis: Leverages the Google Gemini API to perform deep analysis, including:

Extraction of key topics (e.g., architectures, datasets, evaluation methods).

Generation of comparative analysis across multiple papers.

Calculation of research impact metrics (h-index, i10-index, journal tiers).

Interactive UI: A user-friendly web interface built with Streamlit that allows for easy paper uploading, searching, and analysis.

🛠️ Tech Stack
Frontend: Streamlit

Backend: Python

LLM: Google Gemini

Vector Database: ChromaDB

Embeddings: sentence-transformers (all-MiniLM-L6-v2)

PDF Parsing: PyMuPDF

CI/CD: GitHub Actions, Streamlit Community Cloud

📂 Project Structure

ai-research-assistant/
├── .github/
│   └── workflows/
│       └── ci.yml
├── agents/
│   ├── __init__.py
│   ├── pdf_parser.py
│   ├── rag_agent.py
│   └── summarizer.py
├── data/
│   └── sample_pdfs/
├── tests/
│   └── test_app.py
├── utils/
│   ├── __init__.py
│   └── database.py
├── .env
├── .gitignore
├── app.py
├── README.md
└── requirements.txt

⚙️ Local Setup and Installation
Follow these steps to run the project on your local machine.

1. Clone the Repository

git clone https://github.com/DBalakrishna4599/ai-research-assistant.git
cd ai-research-assistant

2. Create and Activate a Virtual Environment

This keeps your project dependencies isolated.

# Create the environment
python3 -m venv venv

# Activate it (on macOS/Linux)
source venv/bin/activate
# On Windows, use: venv\Scripts\activate


3. Install Dependencies

Install all required packages from the requirements.txt file.

pip install -r requirements.txt

4. Set Up Environment Variables

Your Gemini API key is needed to run the summarizer agent.

Create a file named .env in the project root. A template (.env.example) is provided.

Add your API key to the new .env file:
              GOOGLE_API_KEY="YOUR_API_KEY_HERE"

5. Run the Streamlit Application

streamlit run app.py
The application should now be running in your browser at http://localhost:8501.

📖 How to Use the App
Upload Papers: Navigate to the "Upload Papers" section and upload one or more research PDFs.

Search & Analyze: Go to the "Search & Analyze" section. Enter a query to find the most relevant papers from your uploaded library.

Get Insights: For any paper in the search results, click "Analyze Topics" to have the AI agent extract key information using the Gemini API.

Compare: Use the "Comparative Analysis" and "Impact Metrics" sections to get a high-level overview of your research collection.

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📝 License: 
Distributed under the MIT License. See LICENSE for more information.

🙏 Acknowledgments

Streamlit
Google Gemini
ChromaDB
Sentence Transformers

