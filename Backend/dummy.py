from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from logic import PandasAgent  # Your PandasAgent file
import os

# Initialize FastAPI
app = FastAPI(title="Pandas Agent API")

# Allow CORS for testing from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the PandasAgent with your CSV
agent = PandasAgent("C:\\Users\\Deepak\\Desktop\\Agentic Ai Training Code\\Data\\game_cleaned_file.csv")

# Request model
class QuestionRequest(BaseModel):
    question: str

# Test route
@app.get("/test")
def test():
    return {"status": "ok", "message": "Server running"}

# Ask route: generates pandas code, executes it, and returns LLM message
@app.post("/ask")
def ask_question(req: QuestionRequest):
    question = req.question.strip()
    if not question or len(question) < 5:
        return {"status": "Invalid", "message": "Question must be at least 5 characters long."}

    try:
        # 1️⃣ Generate pandas code via LLM
        code = agent.generate_pandas_code(question)

        # 2️⃣ Execute the code
        data_result = agent.execute_code(code)

        # 3️⃣ Ask LLM to summarize or explain results
        prompt = f"""
You are a helpful AI assistant. Here is the data extracted from the dataset:

Data: {data_result}

User asked: {question}

Explain the results in a clear and friendly way.
"""
        llm_response = agent.llm.invoke(prompt)
        llm_msg = llm_response.content.strip()

        # 4️⃣ Return all results
        return {
            "status": "success",
            "generated_code": code,
            "data": data_result,
            "llm_message": llm_msg
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}