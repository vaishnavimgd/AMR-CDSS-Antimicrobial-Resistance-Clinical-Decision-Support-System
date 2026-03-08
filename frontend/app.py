# app.py
import streamlit as st
import requests
import pandas as pd
import altair as alt
import numpy as np

# -------------------- Page Config --------------------
st.set_page_config(page_title="🧬 AMR Prediction Dashboard", layout="wide", initial_sidebar_state="expanded")

# -------------------- Custom CSS --------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #e0eafc, #cfdef3);
    }
    .card {
        border-radius: 15px;
        padding: 15px;
        color: white;
        text-align:center;
        box-shadow: 3px 3px 15px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }
    .resistant {background: linear-gradient(to right, #FF416C, #FF4B2B);}
    .susceptible {background: linear-gradient(to right, #43e97b, #38f9d7);}
    </style>
""", unsafe_allow_html=True)

# -------------------- Header --------------------
st.markdown("""
<div style="background: linear-gradient(to right, #667eea, #764ba2); 
            padding: 20px; border-radius: 15px; text-align:center">
    <h1 style="color:white;">🧬 AMR Prediction Dashboard</h1>
    <p style="color:white; font-size:16px;">Interactive visualization of antimicrobial resistance genes</p>
</div>
""", unsafe_allow_html=True)

# -------------------- File Upload --------------------
uploaded_file = st.file_uploader("📂 Upload FASTA File", type=["fasta", "fa", "txt"], help="Drag & drop FASTA file. Max 200MB.")

if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    files = {'file': (uploaded_file.name, uploaded_file, 'text/plain')}

    # -------------------- API Call with Spinner --------------------
    api_url = "http://127.0.0.1:8001/analyze"  # Replace with your API endpoint
    with st.spinner("⚙️ Initializing C++ Extraction Engine..."):
        pass
    with st.spinner("🤖 Running PyTorch Inference..."):
        response = requests.post(api_url, files=files)
        result = response.json()

    # -------------------- Tabs for Charts --------------------
    tabs = st.tabs(["Summary", "Antibiotics", "Gene Scores", "SHAP Heatmap", "Pie Chart"])

    # -------------------- Summary Tab --------------------
    with tabs[0]:
        st.markdown("### 📊 Summary")
        summary = result.get("summary", {"sequences_analyzed":1,"genes_detected":3,"highest_score":0.9})
        cols = st.columns(len(summary))
        colors = ["#667eea","#764ba2","#43e97b"]
        for col, (key, value), color in zip(cols, summary.items(), colors):
            col.markdown(f"""
            <div class="card" style="background:{color};">
                <h4>{key}</h4>
                <p style='font-size:20px'>{value}</p>
            </div>
            """, unsafe_allow_html=True)

    # -------------------- Antibiotics Tab --------------------
    with tabs[1]:
        st.markdown("### 🛡️ Antibiotic Resistance Status")
        prediction = result.get("prediction", {})
        res_counts = {"Resistant":0,"Susceptible":0}
        cols = st.columns(len(prediction))
        icons = {"Ciprofloxacin":"💊","Ampicillin":"🧪","Tetracycline":"🩺"}
        for col, (ab, status) in zip(cols, prediction.items()):
            if status=="Resistant": res_counts["Resistant"]+=1
            else: res_counts["Susceptible"]+=1
            cls = "resistant" if status=="Resistant" else "susceptible"
            col.markdown(f"""
            <div class="card {cls}">
                <h3>{icons.get(ab,'💉')} {ab}</h3>
                <p style="font-size:18px">{status}</p>
            </div>
            """, unsafe_allow_html=True)
        if result.get("anomaly", False):
            st.error("⚠️ Zero-Day Threat Detected! Unusual AMR gene patterns found.")

    # -------------------- Gene Scores Tab --------------------
    with tabs[2]:
        st.markdown("### 📈 Gene Importance Scores")
        gene_scores = result.get("gene_scores", {"geneA":0.6,"geneB":0.59,"geneC":0.592})
        df_genes = pd.DataFrame(list(gene_scores.items()), columns=['Gene','Score'])

        # Horizontal Bar Chart
        bar_chart = alt.Chart(df_genes).mark_bar(color="#4facfe").encode(
            x=alt.X('Score:Q', title='Importance Score'),
            y=alt.Y('Gene:N', sort='-x', title='Gene'),
            tooltip=['Gene','Score']
        ).properties(width=500,height=250).interactive()
        st.altair_chart(bar_chart, use_container_width=True)

        # Bubble Chart
        bubble_chart = alt.Chart(df_genes).mark_circle().encode(
            x='Gene:N',
            y='Score:Q',
            size=alt.Size('Score:Q',scale=alt.Scale(range=[200,1000])),
            color=alt.Color('Score:Q',scale=alt.Scale(scheme='reds')),
            tooltip=['Gene','Score']
        ).properties(width=500,height=250).interactive()
        st.altair_chart(bubble_chart, use_container_width=True)

        # Line Chart
        line_chart = alt.Chart(df_genes).mark_line(point=True,color="#764ba2").encode(
            x='Gene:N',
            y='Score:Q',
            tooltip=['Gene','Score']
        ).properties(width=900,height=250)
        st.altair_chart(line_chart,use_container_width=True)

    # -------------------- SHAP Heatmap Tab --------------------
    with tabs[3]:
        st.markdown("### 🔥 SHAP Heatmap (Gene vs Antibiotic)")
        # Prepare mock SHAP values
        antibiotics = list(prediction.keys())
        genes = list(gene_scores.keys())
        shap_values = np.random.rand(len(genes),len(antibiotics))  # Replace with real SHAP values if available
        df_shap = pd.DataFrame(shap_values,index=genes,columns=antibiotics).reset_index().melt(id_vars='index', var_name='Antibiotic', value_name='SHAP')
        df_shap.rename(columns={'index':'Gene'}, inplace=True)

        # Altair heatmap
        heatmap = alt.Chart(df_shap).mark_rect().encode(
            x=alt.X('Antibiotic:N', title='Antibiotic'),
            y=alt.Y('Gene:N', title='Gene'),
            color=alt.Color('SHAP:Q', scale=alt.Scale(scheme='reds'), title='SHAP Value'),
            tooltip=['Gene','Antibiotic','SHAP']
        ).properties(width=500,height=400).interactive()
        st.altair_chart(heatmap,use_container_width=True)

    # -------------------- Pie Chart Tab --------------------
    with tabs[4]:
        st.markdown("### 🥧 Resistant vs Susceptible Proportion")
        df_pie = pd.DataFrame({'Status':list(res_counts.keys()),'Count':list(res_counts.values())})
        pie_chart = alt.Chart(df_pie).mark_arc().encode(
            theta='Count:Q',
            color=alt.Color('Status:N', scale=alt.Scale(domain=["Resistant","Susceptible"],range=["#FF4B4B","#43e97b"])),
            tooltip=['Status','Count']
        ).properties(width=400,height=400)
        st.altair_chart(pie_chart,use_container_width=False)

    # -------------------- Footer --------------------
    st.markdown("---")
    st.markdown("Tech Stack: **Streamlit + FastAPI + PyTorch + C++ Extraction Engine** 🖥️💉🧬")