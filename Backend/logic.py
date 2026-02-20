from unittest import result
from langchain_groq import ChatGroq
import pandas as pd
import os
import sys
import io
import numpy as np
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import base64

load_dotenv()

class PandasAgent:
    def __init__(self,csv_url:str):
        self.df  =  pd.read_csv(csv_url)
       
        self.summary  =  f"""
         the data contains{self.df.describe()}  and my data schema are{self.df.columns}  and  the data types are {self.df.dtypes} and the len of my data is {self.df.shape}
    """
        self.llm  = ChatGroq(
                model ="llama-3.1-8b-instant",
                api_key = os.getenv("API_KEY"),
                temperature = 0
            )

        self.memory  = []
    def generate_pandas_code(self,question:str):
        prompt = f"""
You are a Python data analyst using pandas.

DataFrame name: df

Rules:
- Return ONLY executable pandas code.
- Do NOT explain anything.
- Store final output in variable result.
- If the question asks for "best / list / names", return rows not counts.
- Use value_counts() ONLY if the question asks for count.
-  if the data doesnot contain the date it into release_year column it inside have the year it is not structured fromat okay and the date columns format is

Guidelines:
- Use pandas only.
- If filtering by year use pd.to_datetime().
- Use value_counts(), groupby(), sort_values() when needed.
- If top results requested use head().

Dataset columns:
{self.df.columns.tolist()}

Dataset info:
{self.df.dtypes}

Sample rows:
{self.df.head(5).to_dict(orient="records")}

Question:
{question}

Output format:
result = ...
"""
         

        response = self.llm.invoke(prompt)
        self.memory.append(f"User :{question}")
        self.memory.append(f"Data Analyst : {response.content}")
        
        code = response.content.strip()

     
        
        print(code)
     

        
        return response.content
    def execute_code(self,code):
        local_vars= {'df':self.df}
        ##lines = [line.strip()  for line in code.split("\n") if line.strip()]
      
        ##for line in lines:
        code = code.replace("```python", "").replace("```", "").strip()
        ##print("Executing Code:\n", code)
        exec(code,{},local_vars)
        if "result" not in local_vars:
            try:
                eval_res = eval(code,{},{"df":self.df})
                local_vars["result"] = eval_res
            except Exception as e:
                pass
        result = local_vars.get("result",None)
        
        if result is None:
            return "NO res generated"
        if isinstance(result,pd.DataFrame):
            return result.astype(object).to_dict(orient="records")
        if isinstance(result,pd.Series):
            return result.astype(object).to_list()
        if isinstance(result,(np.integer,np.floating)):
            return result.item()
        if isinstance(result,np.ndarray):
            return result.tolist()
        if isinstance(result,pd.Index):
            return result.tolist()
        if isinstance(result,np.dtype):
            return str(result)
        if isinstance(result,(tuple,set)):
            return list(result)
        if isinstance(result,dict):
            clean_dict ={}
            for k,v in result.items():
                if isinstance(v,(np.Integer,np.floating)):
                    clean_dict[k] = v.item()
                elif isinstance(v,np.ndarray):
                    clean_dict[k] = v.tolist()
                elif isinstance(v,np.dtype):
                    clean_dict[k]= str(v)
                else:
                    clean_dict[k] = v
            return clean_dict
        return result
        try:
            import json
            json.dumps(result)
            return result
        except TypeError:
            return str(result)
        
        
    