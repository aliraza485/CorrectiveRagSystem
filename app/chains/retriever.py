import os
import glob
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

def build_ensemble_retriever(docs_path: str = "data") -> RunnableLambda:
    """Loads documents, chunks them, and builds a custom LCEL dense + sparse ensemble retriever."""
    os.makedirs(docs_path, exist_ok=True)
    
    docs: List[Document] = []
    
    for file_path in glob.glob(os.path.join(docs_path, "**/*"), recursive=True):
        if file_path.endswith(".pdf"):
            docs.extend(PyPDFLoader(file_path).load())
        elif file_path.endswith(".txt"):
            docs.extend(TextLoader(file_path, encoding="utf-8").load())
            
    if not docs:
        docs = [Document(page_content="System fallback document. No data loaded.", metadata={"source": "system"})]

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    os.makedirs("vectorstore", exist_ok=True)
    vectorstore.save_local("vectorstore/faiss_index")
    
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    sparse_retriever = BM25Retriever.from_documents(splits)
    sparse_retriever.k = 3

    def ensemble_search(query: str) -> List[Document]:
        """Combines and deduplicates results from dense and sparse retrievers."""
        dense_docs = dense_retriever.invoke(query)
        sparse_docs = sparse_retriever.invoke(query)
        
        seen_content = set()
        combined_docs = []
        for doc in dense_docs + sparse_docs:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                combined_docs.append(doc)
        return combined_docs[:5]

    return RunnableLambda(ensemble_search)