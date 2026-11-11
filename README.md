# 🚀 Production-Grade Corrective & Self-Reflective RAG (CRAG)

A production-ready implementation of a **Corrective & Self-Reflective Retrieval-Augmented Generation (CRAG)** system built with **LangChain Expression Language (LCEL)**, **FastAPI**, **Streamlit**, and **Pydantic v2**.

Unlike standard RAG systems that blindly trust retrieved context and produce hallucinations when document relevance is low, this CRAG pipeline dynamically evaluates document quality. If local retrieved documents fail the relevance threshold, the pipeline automatically rewrites the query, triggers a web search fallback via Tavily, merges context, and synthesizes a verified answer.

---

## 📌 Executive Summary

Standard RAG architectures often fail when vector retrieval fetches irrelevant, outdated, or noisy context. Feeding poor context into an LLM leads to hallucinations and inaccurate responses.

This **CRAG System** solves context unreliability by implementing an automated self-corrective evaluation pipeline:

1. **Hybrid Retrieval**: Combines dense semantic search (FAISS) and sparse keyword search (BM25).
2. **Relevance Grading**: Evaluates each retrieved document chunk using an LLM with structured outputs.
3. **Adaptive Self-Correction & Web Fallback**: If retrieved local context fails evaluation, the pipeline automatically rewrites the user query and executes a real-time web search fallback via the Tavily Search API.
4. **Context Merging & Answer Synthesis**: Merges evaluated context to generate concise, factual answers with traceable source attribution.

---

## 🏗️ Architecture Workflow

```
                   +------------------------+
                   |     User Question      |
                   +-----------+------------+
                               |
                               v
               +---------------+----------------+
               |  EnsembleRetriever             |
               |  (FAISS Dense + BM25 Sparse)   |
               +---------------+----------------+
                               |
                               v
               +---------------+----------------+
               |   Document Relevance Grader   |
               |     (GPT-4o-mini + Pydantic)   |
               +---------------+----------------+
                               |
                   /-----------\-----------\
                  /                         \
        [Relevant Docs Exist]         [All Docs Irrelevant]
                /                             \
               v                               v
    +------------------+             +--------------------+
    | Aggregated Context|             |   Query Rewriter   |
    +--------+---------+             +---------+----------+
             |                                 |
             |                                 v
             |                       +--------------------+
             |                       |   Tavily Search    |
             |                       |   (Web Fallback)   |
             |                       +---------+----------+
             |                                 |
             \----------------+----------------/
                              |
                              v
             +----------------+-----------------+
             |      RAG Answer Generator        |
             |    (GPT-4o-mini + LCEL Chain)    |
             +----------------+-----------------+
                              |
                              v
             +----------------+-----------------+
             |     FastAPI / Streamlit Output    |
             +----------------------------------+
```

---

## 🛠️ Tech Stack

* **LLM & Framework:** LangChain (LCEL primitives only), OpenAI (`gpt-4o-mini`)
* **Retrieval Engine:** Custom Ensemble (FAISS Dense Search + BM25 Sparse Search)
* **Web Fallback:** Tavily Search API
* **Backend API:** FastAPI (Async lifespan management & Pydantic v2 validation)
* **Frontend UI:** Streamlit (Interactive chat with real-time execution log sidebar)
* **Observability:** LangSmith Tracing

---

## 📁 Repository Structure

```text
CorrectiveRagSystem/
├── app/
│   ├── __init__.py
│   ├── config.py          # Environment settings (Pydantic Settings)
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── retriever.py   # EnsembleRetriever (FAISS + BM25)
│   │   ├── grader.py      # LLM Document Relevance Grader chain
│   │   ├── rewriter.py    # Query Optimizer chain for web fallback
│   │   └── generator.py   # RAG Answer Generation chain
│   ├── tools/
│   │   ├── __init__.py
│   │   └── web_search.py  # Tavily Search Tool wrapper
│   └── pipeline.py        # Master CRAG Execution Pipeline (RunnableLambda)
├── data/                  # Local PDFs/TXT documents store
├── vectorstore/           # FAISS index persistence directory
├── main.py                # FastAPI app & POST /api/v1/query endpoint
├── streamlit_app.py       # Streamlit Chat interface & sidebar log viewer
├── requirements.txt       # Project dependencies
├── .gitignore             # Ignored directories (.env, .venv, vectorstore/)
└── README.md              # Project documentation
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites

* Python 3.10+
* Git
* API Keys for OpenAI and Tavily (and optionally LangSmith)

### 2. Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/aliraza485/CorrectiveRagSystem.git
cd CorrectiveRagSystem

# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate on Linux/macOS
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY="sk-..."
TAVILY_API_KEY="tvly-..."

# Optional LangSmith Tracing
LANGCHAIN_API_KEY="ls__..."
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_PROJECT="crag_project"
```

### 5. Add Knowledge Base Documents

Place your local `.pdf` or `.txt` files in the `data/` directory.

---

## 🚀 Running the Application

### Launch FastAPI Backend
In your first terminal tab:

```bash
python -m uvicorn main:app --reload --port 8000
```
*Wait for output:* `Application Startup Complete.`

### Launch Streamlit UI
In a second terminal tab:

```bash
streamlit run streamlit_app.py
```
The browser will automatically open `http://localhost:8501`.

---

## 🔌 API Specification

### Endpoint: `POST /api/v1/query`

#### Request Body
```json
{
  "question": "What is the key contribution of the No-U-Turn Sampler paper?"
}
```

#### Response Body
```json
{
  "answer": "The No-U-Turn Sampler (NUTS) eliminates the need to manually set the step count parameter L in Hamiltonian Monte Carlo by automatically stopping when the trajectory begins to double back on itself.",
  "used_web_search": false,
  "rewritten_query": "",
  "sources": [
    "data/P17-The No-U-Turn Sampler Adaptively Setting Path Lengths.pdf"
  ],
  "raw_context": [
    "We introduce the No-U-Turn Sampler (NUTS), an extension to HMC that eliminates the need to set a number of steps L..."
  ]
}
```

---

## 🧪 Testing Execution Paths

1. **Local Document QA (Passes Relevance Grade):**
   * Ask a question present in your `data/` folder (e.g., about NUTS paper or Attention Is All You Need).
   * **Sidebar Status:** Displays `📄 Local Documents Graded as Relevant`.
   * **Web Search:** `used_web_search: false`.

2. **Web Fallback (Fails Relevance Grade):**
   * Ask a question absent from local files (e.g., *"What is the latest score of the Premier League match today?"*).
   * **Sidebar Status:** Displays `🌐 Web Search Triggered (Local Docs Failed Grade)`.
   * **Web Search:** `used_web_search: true`.
   * **Rewritten Query:** Shows the optimized web search query generated by `rewriter_chain`.

---

## 📊 Observability with LangSmith

If `LANGCHAIN_TRACING_V2=true` is enabled in `.env`, every request automatically registers an execution trace on [LangSmith](https://smith.langchain.com). You can view step-by-step latency, grading decisions, prompt inputs, and token consumption.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.