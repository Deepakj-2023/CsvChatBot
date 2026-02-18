from logic import PandasAgent

agent =  PandasAgent("C://Users//Deepak//Desktop//Agentic Ai Training Code//Data//books_cleaned.csv")

if __name__ == "__main__":
    
    question = "visulaize the year wise  book publishation"
    type = agent.classify_question(question)
    code = agent.generate_pandas_code(question)
    print("Generated Code:\n", code)
    result = agent.execute_code(code)
    print("Execution Result:\n", result)