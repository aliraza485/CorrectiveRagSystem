from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Load env before other local modules
from app.config import settings
from app.chains.retriever import build_ensemble_retriever
from app.pipeline import build_crag_pipeline

# Globals for dependency injection
retriever = None
crag_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever, crag_pipeline
    print("Initializing EnsembleRetriever and building CRAG pipeline...")
    retriever = build_ensemble_retriever("data/")
    crag_pipeline = build_crag_pipeline(retriever)
    print("Application Startup Complete.")
    yield
    print("Shutting down...")

app = FastAPI(title="Production CRAG API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Schemas
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    used_web_search: bool
    rewritten_query: Optional[str] = None
    sources: List[str]
    raw_context: List[str]

@app.post("/api/v1/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    try:
        if not crag_pipeline:
            raise HTTPException(status_code=503, detail="Pipeline not initialized")
            
        result = crag_pipeline.invoke({"question": req.question})
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))