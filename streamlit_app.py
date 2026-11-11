import streamlit as st
import requests
import os

st.set_page_config(page_title="CRAG AI Assistant", page_icon="🤖", layout="wide")

st.title("🤖 Corrective RAG Chat")
st.markdown("Retrieves local documents. Self-corrects via web search if local context is irrelevant.")

API_URL = os.getenv("API_URL", "https://correctiveragsystem.onrender.com/api/v1/query")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_metadata" not in st.session_state:
    st.session_state.latest_metadata = None

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing context & generating response..."):
            try:
                response = requests.post(API_URL, json={"question": prompt})
                response.raise_for_status()
                data = response.json()
                
                answer = data.get("answer", "No answer generated.")
                st.markdown(answer)
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.latest_metadata = data
                
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to communicate with API. Ensure FastAPI is running on {API_URL}")

# Render Execution Sidebar
if st.session_state.latest_metadata:
    with st.sidebar:
        st.header("⚙️ Execution Trace")
        meta = st.session_state.latest_metadata
        
        if meta.get("used_web_search"):
            st.warning("🌐 Web Search Triggered (Local Docs Failed Grade)")
            st.info(f"**Rewritten Query:**\n{meta.get('rewritten_query')}")
        else:
            st.success("📄 Local Documents Graded as Relevant")
            
        st.subheader("🔗 Final Sources")
        for source in meta.get("sources", []):
            st.caption(f"- {source}")
            
        with st.expander("🔍 View Raw Context Chunks"):
            for i, chunk in enumerate(meta.get("raw_context", [])):
                st.markdown(f"**Chunk {i+1}**")
                st.caption(chunk)
                st.divider()

        # Add this inside the sidebar block in streamlit_app.py
with st.sidebar:
    st.header("📥 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files to /data", 
        type=["pdf", "txt"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            file_path = f"data/{file.name}"
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        st.success(f"Saved {len(uploaded_files)} file(s) to data/. Restart FastAPI server to re-index!")