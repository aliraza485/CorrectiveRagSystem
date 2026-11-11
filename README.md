# Corrective RAG (CRAG) Production System

A self-reflective Retrieval-Augmented Generation pipeline using LangChain (LCEL), FastAPI, and Streamlit.
This system automatically evaluates retrieved context quality and self-corrects via query-rewriting and web search (Tavily) if the documents are irrelevant.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt