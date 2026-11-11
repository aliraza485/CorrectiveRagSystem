from typing import Dict, Any, List
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document

from app.chains.grader import grader_chain
from app.chains.rewriter import rewriter_chain
from app.chains.generator import generator_chain
from app.tools.web_search import web_search_tool
from langchain_core.runnables import RunnableLambda


def build_crag_pipeline(retriever: RunnableLambda) -> RunnableLambda:
    """Constructs the master CRAG execution logic as a LangChain RunnableLambda."""
    
    def crag_logic(inputs: Dict[str, Any]) -> Dict[str, Any]:
        question = inputs["question"]
        
        # 1. Retrieve Documents
        docs: List[Document] = retriever.invoke(question)
        
        # 2. Grade Documents
        relevant_docs: List[Document] = []
        for d in docs:
            score = grader_chain.invoke({"question": question, "document": d.page_content})
            if score.binary_score.lower() == "yes":
                relevant_docs.append(d)
                
        used_web_search = False
        search_query = ""
        
        # 3. Conditional Web Search (Fallback)
        if not relevant_docs:
            used_web_search = True
            search_query = rewriter_chain.invoke({"question": question})
            
            search_results = web_search_tool.invoke({"query": search_query})
            
            # Translate raw web results back to Document schemas
            web_docs = [
                Document(page_content=res["content"], metadata={"source": res.get("url", "Tavily")})
                for res in search_results
            ]
            relevant_docs.extend(web_docs)
            
        # 4. Generate Answer
        context_str = "\n\n---\n\n".join([d.page_content for d in relevant_docs])
        answer = generator_chain.invoke({"context": context_str, "question": question})
        
        # Deduplicate sources
        sources = list(set([d.metadata.get("source", "Unknown") for d in relevant_docs]))
        raw_context = [d.page_content for d in relevant_docs]
        
        return {
            "answer": answer,
            "used_web_search": used_web_search,
            "rewritten_query": search_query,
            "sources": sources,
            "raw_context": raw_context
        }

    return RunnableLambda(crag_logic)