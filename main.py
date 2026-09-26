"""Offline-first Zepto policy RAG service; MOCK_LLM defaults to enabled."""
from __future__ import annotations
import os
from pathlib import Path
from typing import TypedDict, Literal
import chromadb
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END

ROOT=Path(__file__).parent; DOCS=ROOT/'docs'; MOCK=os.getenv('MOCK_LLM','1') != '0'
KEYWORDS=('delivery','return','refund','membership','tracking','cancel','gift card','support hours')
PROMPT_TEMPLATE='''ROLE: You are Zepto's policy support assistant.\nCONTEXT: {context}\nTASK: Answer the customer question: {query}\nFORMAT: Return JSON with answer, sources, confidence.\nLENGTH: Use 1–3 concise sentences.\nCONSTRAINT: Do not answer using information not present in the provided context.\nEXAMPLE: Context: Gift cards are valid one year. Question: How long are gift cards valid? Answer: {"answer":"Gift cards are valid for one year.","sources":["doc_07"],"confidence":1.0}\n'''
class AskRequest(BaseModel): query:str=Field(min_length=1)
class Answer(BaseModel): answer:str; sources:list[str]; confidence:float=Field(ge=0,le=1)
class State(TypedDict, total=False): query:str; intent:Literal['policy_question','general_question']; context:list[str]; source_ids:list[str]; response:Answer

model=SentenceTransformer('all-MiniLM-L6-v2')
client=chromadb.PersistentClient(path=str(ROOT/'chroma_db')); collection=client.get_or_create_collection('zepto_policies',metadata={'hnsw:space':'cosine'})
def ingest():
    docs=sorted(DOCS.glob('doc_*.txt')); ids=[p.stem for p in docs]
    if collection.count()!=len(docs):
        collection.upsert(ids=ids,documents=[p.read_text(encoding='utf8') for p in docs],embeddings=model.encode([p.read_text(encoding='utf8') for p in docs]).tolist(),metadatas=[{'source':i} for i in ids])
def classify_intent(s:State):
    # MOCK branch is deterministic; optional real branch is deliberately isolated for a provider implementation.
    q=s['query'].lower(); intent='policy_question' if any(k in q for k in KEYWORDS) else 'general_question'
    return {'intent':intent}
def retrieve_and_answer(s:State):
    result=collection.query(query_embeddings=[model.encode(s['query']).tolist()],n_results=3,include=['documents'])
    docs=result['documents'][0]; ids=result['ids'][0]
    if MOCK: answer=f'Based on the retrieved context: {docs[0][:200]}'
    else: answer=real_llm_with_retries(PROMPT_TEMPLATE.format(context='\n'.join(docs),query=s['query']))
    return {'context':docs,'source_ids':ids,'response':Answer(answer=answer,sources=ids,confidence=1.0 if MOCK else .8)}
def direct_answer(s:State):
    answer='I can only answer questions about Zepto policies right now.' if MOCK else real_llm_with_retries(PROMPT_TEMPLATE.format(context='',query=s['query']))
    return {'response':Answer(answer=answer,sources=[],confidence=1.0 if MOCK else .5)}
def real_llm_with_retries(prompt:str)->str:
    """Optional extension hook. Validate/retry raw provider output up to three total attempts."""
    last='Real LLM backend is not configured.'
    for _ in range(3):
        try: return Answer.model_validate_json(last).answer # replace `last` with provider raw JSON
        except Exception: last='{"answer":"Real LLM response failed validation; please emit valid JSON.","sources":[],"confidence":0.0}'
    return 'ERROR: real LLM output could not be validated.'
def route(s:State): return 'retrieve_and_answer' if s['intent']=='policy_question' else 'direct_answer'
ingest(); graph=StateGraph(State); graph.add_node('classify_intent',classify_intent); graph.add_node('retrieve_and_answer',retrieve_and_answer); graph.add_node('direct_answer',direct_answer); graph.set_entry_point('classify_intent'); graph.add_conditional_edges('classify_intent',route); graph.add_edge('retrieve_and_answer',END); graph.add_edge('direct_answer',END); app=FastAPI(title='Zepto Policy Assistant'); workflow=graph.compile()
@app.post('/ask',response_model=Answer)
def ask(request:AskRequest)->Answer: return workflow.invoke({'query':request.query})['response']
