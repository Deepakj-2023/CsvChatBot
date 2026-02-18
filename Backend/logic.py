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

import base64

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
1. 1. Never call .str or .list() on a grouped Series (SeriesGroupBy).
   - If you need to split strings, do it BEFORE grouping using df['col'].str.split(',').
   - After grouping, always use .apply(lambda x: list(x)) to convert to lists.
2. If aggregating authors, split comma-separated strings using str.split(',').explode() before converting to list.
3. When counting books per year, use aggregation functions like 'count' on a column like title.
4. Always reset index after groupby if needed to have columns accessible.
5. For top N, use .sort_values(...) and .head(N).
6.Do NOT chain .str on groupby objects.



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
        
        
    def classify_question(self, question: str):

        q = question.lower()
        vis_keys  = ["visualize","visualization","graph","plot","chart","histogram","scatter","line","bar","distribution"]
        if any(key in q for key in vis_keys):
            return "visualization"

        
        for col in self.df.columns:
            if col.lower() in q:
                return "data_question"

       
        try:
            prompt = f"""
           You are a Python data analyst
           
            Classify the question into one of three categories:
            - data_question  : questions that ask for computing , grouping ,filtering ,counting data and displaying the data.
            - visualization : question that ask to plot or visualize the data like graph ,plot ,chart ,histogram,scatter,line,bar etc  this type of question is visualization question
            - normal_chat :  causal converation (hii,how are you ,greetings etc)
            
            Question: {question}
            Only respond with one word: data_question, visualization, or normal_chat.
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
        
    def generate_pandasvis_code(self,question:str):
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
1. 1. Never call .str or .list() on a grouped Series (SeriesGroupBy).
   - If you need to split strings, do it BEFORE grouping using df['col'].str.split(',').
   - After grouping, always use .apply(lambda x: list(x)) to convert to lists.
2. If aggregating authors, split comma-separated strings using str.split(',').explode() before converting to list.
3. When counting books per year, use aggregation functions like 'count' on a column like title.
4. Always reset index after groupby if needed to have columns accessible.
5. For top N, use .sort_values(...) and .head(N).
6.Do NOT chain .str on groupby objects.
7.Do not use this name for new varible cration okay because this columns okay {self.df.columns.tolist()}
8.7. NEVER use pivot(). Always use pivot_table() with fill_value=0 to avoid duplicate index errors.




CRITICAL RULE:
You MUST assign final output to variable named result.
If result variable is missing, the system will fail.
- Always group, aggregate, or transform as needed to fully answer the question.
- If the question asks for counts or lists, use groupby, agg, or value_counts appropriately
Always follow this template:
Important Task:
    1 .Generate pandas code for visualization question dataset
    2.To generate the matplotlib or seaborn code for visualization question and assign the final output to variable named result.
IMPORTANT:
- DO NOT use df.plot() or pandas .plot().
- Use matplotlib (plt.bar, plt.plot, plt.hist, plt.scatter etc.)
- Always start with plt.figure(figsize=(10,6))
- Assign final result = "plot_created"
CRITICAL PIVOT RULE:
- NEVER use pivot()
- ALWAYS use pivot_table(index=..., columns=..., values=..., fill_value=0)

VISUALIZATION RULES:
- Use ONLY matplotlib (plt.bar, plt.plot, plt.hist, plt.scatter)
- NEVER use df.plot()
- NEVER use seaborn
- Always start with: plt.figure(figsize=(10,6))
- Always assign: result = "plot_created"




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

     
        
        print(code)
     

        
        return response.content
    def execute_visualization_code(self,code :str):
        """ 
          Executes code for visualization questions.
          Returns a base64 string of the figure.
        """
        local_vars ={"df":self.df.copy(),
                     "plt":plt,
                     "np":np,
                     "pd":pd
                     }
       
        
        code = code.replace("```python","").replace("```","").strip()
        if ".pivot(" in code:
            code = code.replace(".pivot(",".pivot_table(fill_value=0,")
            if "fill_value" not in code:
                code = code.replace(")",", fill_value=0)")
        try: 
            plt.clf()     
            exec(code,{},local_vars)
            buf = io.BytesIO()
            plt.savefig(buf,format="png")
            buf.seek(0)
            plt.close()
            
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            return img_base64
        except Exception as e:
            plt.close()
            return f"ERROR: {str(e)}"
    
            
        
