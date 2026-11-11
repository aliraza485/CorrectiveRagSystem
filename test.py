# seed_data.py
import os
import urllib.request

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Sample 1: Write a custom text document
sample_text = """
The Quantum Engine project started in Q1 2025 with a budget of $2.5 Million.
The primary objective is to optimize RAG latency under 200ms using hybrid vector search.
Lead Engineer: Sarah Connor.
Key Risk: Tavily API rate limits during high-throughput query fallback.
"""

with open(os.path.join(DATA_DIR, "quantum_engine_notes.txt"), "w", encoding="utf-8") as f:
    f.write(sample_text)

print("✅ Sample text file created in data/ quantum_engine_notes.txt")

# Sample 2: Download a public sample PDF (e.g., Attention Is All You Need paper)
pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"
pdf_path = os.path.join(DATA_DIR, "attention_is_all_you_need.pdf")

if not os.path.exists(pdf_path):
    print("📥 Downloading sample PDF from arXiv...")
    urllib.request.urlretrieve(pdf_url, pdf_path)
    print("✅ Downloaded attention_is_all_you_need.pdf into data/")