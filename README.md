# MCP-Doc-QnA

A simple Document Q&A server and Python client built with the Model Context Protocol (MCP) and the OpenAI API. Upload PDF files, ask questions, and view both answers and your query history.

## Features

- **PDF Upload**: Extract text from PDFs using PyPDF2 and store it in a SQLite database.  
- **Document Listing**: List all uploaded document IDs as JSON.  
- **Question & Answer**: Send document content and a question to the GPT-4O-mini model, store and return the answer.  
- **Query History**: Retrieve a history of all past questions and answers via a `history://list` resource.  
- **Stateless HTTP**: Each HTTP request is handled independently—no persistent session or extra auth required in development.  

## Requirements

- Python 3.10 or higher  
- A valid OpenAI API key  
- Git

## Getting Started

1. **Clone the repository**  
   ```bash
   git clone https://github.com/<your-username>/mcp-doc-qna.git
   cd mcp-doc-qna

2-Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate


3-Install dependencies
pip install -r requirements.txt


4-Configure environment variables
cp .env.example .env
# Then edit .env and set:
# OPENAI_API_KEY=sk-...
# MCP_SERVER_URL=http://localhost:8000
# DANGEROUSLY_OMIT_AUTH=true  (development only)


5-Initialize the database
python init_db.py

Running the Server
python server.py
You should see output like:
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


You will see:
Confirmation that the PDF loaded successfully.
A list of uploaded document IDs.
The model’s summary answer to “Can you summarize this document?”
A printed history of all past queries and answers.

