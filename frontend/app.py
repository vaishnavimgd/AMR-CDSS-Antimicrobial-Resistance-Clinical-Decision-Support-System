import streamlit as st
import requests

st.title("AMR Prediction Dashboard")

uploaded_file = st.file_uploader("Upload file")

if uploaded_file:

    files = {"file": uploaded_file.getvalue()}

    response = requests.post(
        "http://127.0.0.1:8001/analyze",
        files={"file": uploaded_file}
    )

    if response.status_code == 200:

        data = response.json()

        st.success("Prediction Completed")

        st.write("File:", data["filename"])
        st.write("Results:")

        for drug, result in data["prediction"].items():
            st.write(f"{drug}: {result}")

    else:
        st.error("Error connecting to API")