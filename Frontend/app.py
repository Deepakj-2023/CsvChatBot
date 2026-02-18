
import streamlit  as st 
import requests
import pandas as pd
import base64
from io import BytesIO
from PIL import Image
st.title("Welcome Csv ChatBot")
st.sidebar.header("Dataset Infromation")
##   strating here......
info_res = requests.get("http://127.0.0.1:8002/dataset_info")
### sider bar code .......
if info_res.status_code ==200:
    info =  info_res.json()
    ## section1 .....
    summary_df = pd.DataFrame({
         "Metric" :["No of Rows","No of Columns"],
         "Value" :[info["rows"],info["columns"]]
    })
    st.sidebar.subheader("Dataset Summary")
    st.sidebar.table(summary_df)
    
    ## sections 2....
    cols_dff=  pd.DataFrame({
        "Column Name": info["column_names"],
        "Data Type": [dtype for dtype in info["data_types"].values()]   
    })
    st.sidebar.subheader("Column Details")  
    st.sidebar.table(cols_dff)


#### above code completed for the  sidebar section and loading the data okay.....
### main code ........
question  = st.text_input("Enter your question about the dataset")

if st.button("Submit"):
   if not question.strip():
       st.warning("Please enter a valid question.")
   else:
       res  =  requests.post("http://127.0.0.1:8002/ask",json={"question": question})
       
       if res.status_code ==200:
          data = res.json()
          if data["status"] == "Success":
              if isinstance(data["data"],list):
                  df_result = pd.DataFrame(data["data"])
                  st.dataframe(df_result)
              elif data["type"] == "visualization":
                  img_base64 = data.get("data") 
                  if img_base64:
                      img_bytes = BytesIO(base64.b64decode(img_base64))
                      img = Image.open(img_bytes)
                      st.image(img)
                  else:
                      st.warning("Visualization image not found")
                                                                            
              else:
                  st.write(data["data"])
          else:
            st.warning(f"Error: {data['message']}")
       else:
           st.error("Failed to get response from the server.")