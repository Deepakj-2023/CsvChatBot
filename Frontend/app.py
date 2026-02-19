import streamlit as st
import requests
import pandas as pd
import base64
from io import BytesIO
from PIL import Image


st.set_page_config(page_title="CSV ChatBot", layout="wide")


st.markdown("""
    <style>
    /* Main Table Styling */
    .main-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-family: sans-serif;
        background-color: #000000; /* Pure Black Background */
        color: #ffffff; /* White Text */
        border: 1px solid #444444;
    }
    .main-table th {
        background-color: #1a1a1a; /* Dark Gray Header */
        color: #ffffff;
        text-align: left;
        padding: 12px 15px;
        border: 1px solid #444444;
    }
    .main-table td {
        padding: 10px 15px;
        border: 1px solid #333333;
        color: #eeeeee;
    }
    /* Subtle hover effect for rows */
    .main-table tr:hover {
        background-color: #222222;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Welcome CSV ChatBot")
st.sidebar.header("Dataset Information")

BASE_URL = "http://127.0.0.1:8002"


def render_html_table(data):
    try:
        df = pd.DataFrame(data)
        if df.empty:
            st.info("The result is empty.")
            return
      
        html = df.to_html(classes='main-table', index=False, escape=False)
        st.markdown(html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error rendering table: {e}")


try:
    info_res = requests.get(f"{BASE_URL}/dataset_info", timeout=5)
    
    if info_res.status_code == 200:
        info = info_res.json()

        st.sidebar.subheader("Summary")
        st.sidebar.write(f"**Rows:** `{info.get('rows', 'N/A')}`")
        st.sidebar.write(f"**Columns:** `{info.get('columns', 'N/A')}`")

        st.sidebar.subheader("Column Details")
        
        column_names = info.get("column_names", [])
        raw_types = info.get("data_types", {})
        
        if column_names:
            
            for col in column_names:
                dtype = str(raw_types.get(col, "unknown"))
                st.sidebar.write(f"🔹 **{col}**: `{dtype}`")
        else:
            st.sidebar.warning("No columns found.")
    else:
        st.sidebar.error("Could not fetch dataset info.")
except Exception as e:
    st.sidebar.error(f"Backend Offline: {e}")

## main logic here only starts from here ......
question = st.text_input("Ask a question about your data:", placeholder="e.g. show me first 10 rows")

if st.button("Submit Query", type="primary"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Processing..."):
            try:
                res = requests.post(
                    f"{BASE_URL}/ask",
                    json={"question": question},
                    timeout=30
                )

                if res.status_code != 200:
                    st.error(f"Server error ({res.status_code}).")
                else:
                    data = res.json()
                    if data.get("status") != "Success":
                        st.warning(data.get("message", "Request failed."))
                    else:
                        resp_type = data.get("type")
                        resp_content = data.get("data")

                        if resp_type == "table":
                            render_html_table(resp_content)
                        elif resp_type == "visualization":
                            if resp_content:
                                img_data = base64.b64decode(resp_content)
                                st.image(Image.open(BytesIO(img_data)), use_container_width=True)
                        else:
                            st.info(str(resp_content))
            except Exception as e:
                st.error(f"Communication Error: {e}")

