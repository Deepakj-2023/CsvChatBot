CSVbot: AI-Powered Data Analyst

CSVbot is an intelligent data exploration tool that allows you to chat with your CSV files. By combining FastAPI, Streamlit, and Llama 3.3 (via Groq), it transforms natural language questions into executable Python code, generates insightful tables, and creates beautiful Matplotlib visualizations on the fly.

Features :
- *Natural Language Querying*: Ask questions about your data in plain English.
- *Automated Code Generation*: Automatically generates and executes pandas code to retrieve information.
- *Data Explanation*: Provides clear, human-like summaries of complex data results.
- *REST API*: Built with FastAPI for easy integration with other tools and frontends.
- *Efficient Performance*: Uses Groq's high-speed inference for near-instant responses.

Tech Stack
 -*Frontend*: Streamlit (Python)
 -*Backend*: FastAPI, Uvicorn
 -*AI Integration*: LangChain, LangChain-Groq
 -*LLM*: llama-3.1-8b-instant 
 -*Visualization*: Matplotlib
 -*Data Processing*: Pandas
 -*Environment Management*: UV, python-dotenv

Setup Instructions
 1. Clone the Repository

Bash

 git clone https://github.com/MSDeepak718/CSVbot.git

 cd CSVbot

 2. Configure Environment Variables

 Create a .env file in the backend directory:

 GROQ_API_KEY=your_groq_api_key_here

 3. Install Dependencies
 Using uv for high-speed installation:

 Bash

 uv sync

How to Run :

The project runs in two separate parts. Ensure you have your CSV file (e.g., books_cleaned.csv) inside the backend folder.

Backend (FastAPI Server)

  Open a terminal and run:

  Bash

  cd backend

  uv run uvicorn main:app --reload --port 8002

  API URL: http://127.0.0.1:8002

  Docs: http://127.0.0.1:8002/docs

Frontend (Streamlit UI)

  Open a second terminal and run:

  Bash

  cd frontend

  uv run streamlit run app.py

  UI URL: http://localhost:8501