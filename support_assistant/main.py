import os
import glob
from typing import List, TypedDict
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END

# Setup & Ingestion
docs_dir = "docs"
collection_name = "zepto_policies"
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name=collection_name)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

if collection.count() == 0:
    doc_files = glob.glob(os.path.join(docs_dir, "doc_*.txt"))
    for file_path in doc_files:
        doc_id = os.path.basename(file_path).replace(".txt", "")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        embedding = embedder.encode(content).tolist()
        collection.add(documents=[content], embeddings=[embedding], ids=[doc_id])

# Graph State
class GraphState(TypedDict):
    query: str
    intent: str
    answer: str
    sources: List[str]
    confidence: float

# Nodes (MOCK_LLM Baseline)
def classify_intent(state: GraphState):
    query = state["query"].lower()
    keywords = ["delivery", "return", "refund", "membership", "tracking", "cancel", "gift card", "support hours"]
    if any(kw in query for kw in keywords):
        return {"intent": "policy_question"}
    return {"intent": "general_question"}

def retrieve_and_answer(state: GraphState):
    query = state["query"]
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    retrieved_docs = results["documents"][0]
    retrieved_ids = results["ids"][0]
    top_chunk_snippet = retrieved_docs[0][:200] if retrieved_docs else ""
    answer = f"Based on the retrieved context: {top_chunk_snippet}..."
    return {"answer": answer, "sources": retrieved_ids, "confidence": 1.0}

def direct_answer(state: GraphState):
    return {"answer": "I can only answer questions about Zepto policies right now.", "sources": [], "confidence": 1.0}

def route_query(state: GraphState):
    if state["intent"] == "policy_question":
        return "retrieve_and_answer"
    return "direct_answer"

# Build Graph
workflow = StateGraph(GraphState)
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_and_answer", retrieve_and_answer)
workflow.add_node("direct_answer", direct_answer)
workflow.set_entry_point("classify_intent")
workflow.add_conditional_edges("classify_intent", route_query, {"retrieve_and_answer": "retrieve_and_answer", "direct_answer": "direct_answer"})
workflow.add_edge("retrieve_and_answer", END)
workflow.add_edge("direct_answer", END)
app_graph = workflow.compile()

# FastAPI App
app = FastAPI(title="Zepto Support Assistant")
class AskRequest(BaseModel):
    query: str
class AskResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    final_state = app_graph.invoke({"query": request.query})
    return AskResponse(answer=final_state["answer"], sources=final_state.get("sources", []), confidence=final_state.get("confidence", 1.0))
