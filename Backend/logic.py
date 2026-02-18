from unittest import result
from langchain_groq import ChatGroq
import pandas as pd
import os
import sys
import io
import numpy as np


class PandasAgent:
    def __init__(self,csv_url:str):
        self.df  =  pd.read_csv(csv_url)
        self.summary  =  f"""
         the data contains{self.df.describe()} and my data schema are{self.df.columns}  and  the data types are {self.df.dtypes} and the len of my data is {self.df.shape}
    """
        self.llm  = ChatGroq(
                model ="llama-3.1-8b-instant",
                api_key ="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",
                    temperature = 0
            )

        self.memory  = []
    def generate_pandas_code(self,question:str):
        prompt  =prompt = f"""
You are a Python data analyst.pandas ≥2.0

DataFrame name is df.

Rules:
- Generate ONLY valid pandas code.
- Do NOT use print().
- Store final output in variable named result.
- Do NOT explain anything.
- Return only executable Python code.
CRITICAL GUIDELINES:
1. Never call .list() on a grouped Series (SeriesGroupBy). Instead, use .agg() or .apply(lambda x: list(...)).
2. If aggregating authors, split comma-separated strings using str.split(',').explode() before converting to list.
3. When counting books per year, use aggregation functions like 'count' on a column like title.
4. Always reset index after groupby if needed to have columns accessible.
5. For top N, use .sort_values(...) and .head(N).


CRITICAL RULE:
You MUST assign final output to variable named result.
If result variable is missing, the system will fail.
- Always group, aggregate, or transform as needed to fully answer the question.
- If the question asks for counts or lists, use groupby, agg, or value_counts appropriately
Always follow this template:

result = <your pandas expression here>



Dataset Summary:
{self.summary}

Question:
{question}
"""        
         

        response = self.llm.invoke(prompt)
        self.memory.append(f"User :{question}")
        self.memory.append(f"Data Analyst : {response.content}")
        
        code = response.content.strip()

        print("\n" + "="*50)
        #print("🧠 QUESTION:", question)
        ##print("📝 GENERATED CODE:\n")
        print(code)
       ## print("="*50 + "\n")

        
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
        
        
    def classify_question(self, question: str):

        q = question.lower()

        # # 1️⃣ Visualization keywords rule
        # viz_keywords = ["plot", "chart", "graph", "bar", "histogram", "line", "pie"]
        # if any(word in q for word in viz_keywords):
        #     return "visualization"

        # # 2️⃣ Column name rule
        # for col in self.df.columns:
        #     if col.lower() in q:
        #         return "data_question"

        # 3️⃣ Fallback to LLM
        try:
            prompt = f"""
            i giving my dataset information and i helps to  easy your classification okay 
                Data Columns  : {self.df.columns}
                Data Schema : {self.summary} and DATA Types : {self.df.dtypes}
                Sample Data : {self.df.head()}
            Classify into one word:
            - data_question 
            - visualization : keywords like visualization  ,graph ,plot  , graph etc  this type of question is visualization question
            - normal_chat :  it means like hii , how are you  this okay 
            
            Question: {question}
            only give this 3 types one words and dont add any extra think okay
            """
            res = self.llm.invoke(prompt)
        ## print("question type is here",res.content.strip().lower() ,flush=True )
            cat =  res.content.strip().lower()
            cat  = cat.replace("*","").replace("-","").strip()
            print(cat)
            if "data_question" in cat:
                return "data_question"
            elif "visualization" in cat:
                return "visualization"
            elif "normal_chat" in cat:
                return "normal_chat"
            else:
                return "normal_chat"
        except Exception as e:
            print(f"Error classifying question: {e}")
            return "normal_chat"
            
        
