import os
import pandas as pd
import numpy as np
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class PandasAgent:
    def __init__(self, csv_url: str):
      
        self.df = pd.read_csv(csv_url)

        
        self.summary = f"""
        Data Description: {self.df.describe()}
        Columns: {self.df.columns.tolist()}
        Data Types: {self.df.dtypes.to_dict()}
        Shape: {self.df.shape}
        """

        
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("API_KEY"),
            temperature=0
        )

       
        self.memory = []

    def generate_pandas_code(self, question: str):
        """
        Generate executable pandas code for a given question using LLM.
        """
        prompt = f"""
You are a Python data analyst using pandas.

DataFrame name: df

Rules:
- Return ONLY executable pandas code.
- Do NOT explain anything.
- Store final output in variable 'result'.
- Use value_counts() only for counts.
- Use pandas only.

Dataset columns:
{self.df.columns.tolist()}

Dataset info:
{self.df.dtypes.to_dict()}

Sample rows:
{self.df.head(5).to_dict(orient='records')}

Question:
{question}

Output format:
result = ...
"""
        response = self.llm.invoke(prompt)
        self.memory.append(f"User: {question}")
        self.memory.append(f"Data Analyst: {response.content}")
        code = response.content.strip()
        print("Generated Code:\n", code)
        return code

    def execute_code(self, code: str):
        """
        Execute pandas code string safely and return structured results.
        """
        local_vars = {'df': self.df}
        code = code.replace("```python", "").replace("```", "").strip()

        try:
            exec(code, {}, local_vars)
        except Exception:
            try:
                eval_res = eval(code, {}, {'df': self.df})
                local_vars['result'] = eval_res
            except Exception as e:
                return f"Error executing code: {str(e)}"

        result = local_vars.get('result', None)

        if result is None:
            return "No result generated"

        
        if isinstance(result, pd.DataFrame):
            return result.astype(object).to_dict(orient="records")
        if isinstance(result, pd.Series):
            return result.astype(object).to_list()
        if isinstance(result, (np.integer, np.floating)):
            return result.item()
        if isinstance(result, np.ndarray):
            return result.tolist()
        if isinstance(result, pd.Index):
            return result.tolist()
        if isinstance(result, dict):
            clean_dict = {}
            for k, v in result.items():
                if isinstance(v, (np.integer, np.floating)):
                    clean_dict[k] = v.item()
                elif isinstance(v, np.ndarray):
                    clean_dict[k] = v.tolist()
                else:
                    clean_dict[k] = v
            return clean_dict
        if isinstance(result, (tuple, set)):
            return list(result)

        return result