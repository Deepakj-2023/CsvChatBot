from fastapi  import FastAPI
from pydantic import BaseModel
import pandas as pd
from logic import PandasAgent

app = FastAPI(title="DEEPAK TEST SERVER 999")
agent =  PandasAgent("C://Users//Deepak//Desktop//Agentic Ai Training Code//Data//books_cleaned.csv")
class QuestionRequest(BaseModel):
    question :str

import os
print("RUNNING FILE PATH:", os.path.abspath(__file__))

@app.get("/test")
def test():
    return {"hello": "world"}
@app.post("/ask")
def ask_question(req :QuestionRequest):
    
    ##return {"hello": "world"}
    
    question  =  req.question.strip()
    if not question or len(question)<5:
        return{
            "status": "Invalid",
            "message": "Question must be at least 5 characters long."
        }
    try:
       cat  =  agent.classify_question(req.question)
       if cat=="normal_chat":
           return{
                "status" :"Normal Chat",
                "message" :"Sorry ,please ask question realted to the data "
           }
       elif cat=="data_question":
        code = agent.generate_pandas_code(req.question)
        print("Generated Code:", code)
        result = agent.execute_code(code)
        print("Execution Result:", result)
        return {
            "status": "Success",
            "type" :"table",
            "generated_code" : code,
            "data" : result
            }
       elif cat =="visualization":
           code =  agent.generate_pandasvis_code(req.question)
           img_base64  =  agent.execute_visualization_code(code)
           return {
                 "status" : "Success",
                 "type" : "visualization",
                 "generated_code":code,
                 "data" : img_base64
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

@app.get("/dataset_info")
def dataset_info():
    df  =  agent.df
    return {
      "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names" : list(df.columns),
        "data_types" :{
             col : str(dtype) for col,dtype in df.dtypes.items()
        }
    }