# Zepto Data & AI Platform Capstone

This repository contains three internally-linked modules for the Zepto Data & AI Platform Capstone.

## Setup and Run Instructions
1. **Install dependencies:** `pip install -r requirements.txt`
2. **Module 1 (Data Pipeline):** Run `python data_pipeline/pipeline.py` or execute the notebook.
3. **Module 2 (Analytics):** Execute `analytics/analysis.py` or the notebooks to generate EDA and the fitted joblib pipeline.
4. **Module 3 (Support Assistant):** Navigate to `support_assistant/` and run `uvicorn main:app --port 8000`. 

## Module 1 Notes
* **Currency Baseline:** The fixed currency conversion rate used is exactly **1 GBP = 105.50 INR**.
* **Missing values:** Handled via median imputation for numeric fields and row dropping for missing text, as documented in the scripts.

## Module 2 Notes
* See `analytics/results.md` for full EDA interpretations, correlation conclusions, and the final model evaluation tables.
* The best pipeline is saved as `artifacts/best_pipeline.joblib`.

## Module 3 Notes (RAG Architecture)
* **Ingestion & Embedding:** The 8 text documents are chunked and embedded locally using `sentence-transformers` (`all-MiniLM-L6-v2`) and stored in a local `chromadb` collection.
* **Routing:** A LangGraph node (`classify_intent`) routes the query based on keywords.
* **Retrieval & Generation:** 
  * Policy questions route to `retrieve_and_answer`, which queries ChromaDB via cosine similarity. 
  * General questions route to `direct_answer`.
  * **MOCK_LLM Branching:** Under the default mock state, no LLM API is called. `retrieve_and_answer` returns a deterministic templated string using the top chunk, and `direct_answer` returns a canned fallback string.

### Example Calls (MOCK_LLM=1)
**Policy Question (Retrieval):**
