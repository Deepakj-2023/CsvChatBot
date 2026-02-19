from fastapi  import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from logic import PandasAgent


app = FastAPI(title="DEEPAK TEST SERVER 999")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent =  PandasAgent("C://Users//Deepak//Desktop//Agentic Ai Training Code//Data//books_cleaned.csv")
class QuestionRequest(BaseModel):
    question :str

import os
print("RUNNING FILE PATH:", os.path.abspath(__file__))

@app.get("/test")
def test():
    return {"hello": "world"}
@app.post("/ask")
def ask_question(req: QuestionRequest):
    question = req.question.strip()
    if not question or len(question) < 5:
        return {
            "status": "Invalid",
            "message": "Question must be at least 5 characters long."
        }
    try:
        # Classify question
        cat = agent.classify_question(question)

        if cat == "normal_chat":
            # Normal chat goes directly to LLM
            code  =  agent.generate_pandas_code(question)
            print("Generated Code:\n", code)
            Result = agent.execute_code(code)
            print("Execution Result:\n", Result) 
            prompt = f"You are a helpful AI assistant. Answer the user's question:\nUser: {question} and based the answer on the following data result: {Result}"
            llm_response = agent.llm.invoke(prompt)
            return {
                "status": "Normal Chat",
                "message": llm_response.content.strip()
            }

        elif cat == "data_question":
            # Generate Pandas code
            code = agent.generate_pandas_code(question)
            print("Generated Pandas Code:\n", code)

            # Execute Pandas code
            data_result = agent.execute_code(code)
            print("Data Result:\n", data_result)

            # Send results + question to LLM for explanation
            prompt = f"""
You are a helpful AI assistant. Here is some data extracted from a dataset:

Data: {data_result}

User asked: {question}

Explain the results in a clear and friendly way, summarizing or suggesting insights as needed.
"""
            llm_response = agent.llm.invoke(prompt)

            return {
                "status": "Success",
                "type": "table",
                "generated_code": code,
                "data": data_result,
                "llm_message": llm_response.content.strip()
            }

        elif cat == "visualization":
            code = agent.generate_pandasvis_code(question)
            img_base64 = agent.execute_visualization_code(code)
            return {
                "status": "Success",
                "type": "visualization",
                "generated_code": code,
                "data": img_base64
            }

        else:
            return {
                "status": "Error",
                "message": f"Unknown category: {cat}"
            }

    except Exception as e:
        return {
            "status": "Error",
            "message": str(e)
        }
