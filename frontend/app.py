import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AMR Dashboard", layout="wide")

st.title("Antimicrobial Resistance Prediction Dashboard")

st.write("Upload a FASTA file to analyze antimicrobial resistance genes.")

# File uploader
uploaded_file = st.file_uploader("Upload FASTA File", type=["fasta", "fa", "txt"])

if uploaded_file is not None:

    st.success("File uploaded successfully")

    try:
        # Send file to FastAPI backend
        response = requests.post(
            "http://127.0.0.1:8001/analyze",
            files={"file": uploaded_file}
        )

        result = response.json()

        st.subheader("Raw Prediction Result")
        st.json(result)

        # Example data for dashboard visualization
        data = pd.DataFrame({
            "Gene": ["geneA", "geneB", "geneC"],
            "Resistance Score": [0.8, 0.6, 0.9]
        })

        st.subheader("AMR Gene Prediction Table")
        st.dataframe(data)

        # Dashboard metrics
        col1, col2, col3 = st.columns(3)

        col1.metric("Sequences analyzed", 1)
        col2.metric("AMR genes detected", len(data))
        col3.metric("Highest score", max(data["Resistance Score"]))

        # Chart
        st.subheader("Resistance Gene Scores")
        st.bar_chart(data.set_index("Gene"))

        # Download button
        csv = data.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Results",
            csv,
            "amr_results.csv",
            "text/csv"
        )

    except:
        st.error("Cannot connect to backend. Please start the FastAPI server.")