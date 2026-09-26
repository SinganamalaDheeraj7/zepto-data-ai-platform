# Support assistant

Install `pip install -r requirements.txt`, then run `uvicorn main:app --reload --port 7860`. Mock mode is the default (`MOCK_LLM` unset or `1`); it makes no LLM network calls. Try:

`curl -X POST http://127.0.0.1:7860/ask -H "Content-Type: application/json" -d '{"query":"What is the delivery fee?"}'`

Expected raw JSON is shaped as `{"answer":"Based on the retrieved context: Zepto delivers ...","sources":["doc_01",...],"confidence":1.0}`. For `{"query":"What is the capital of France?"}`, it is `{"answer":"I can only answer questions about Zepto policies right now.","sources":[],"confidence":1.0}`.

Architecture: **ingestion** reads the eight `docs/doc_*.txt` files in `ingest`; **embedding** uses local `all-MiniLM-L6-v2`; **storage/retrieval** uses the persistent Chroma collection `zepto_policies`, queried by the `retrieve_and_answer` LangGraph node; **generation** occurs in `retrieve_and_answer` or `direct_answer`. `classify_intent` conditionally routes between them. The default mock branches use a keyword classifier and deterministic canned responses; the optional `MOCK_LLM=0` branches use the included role/context/task/format/length prompt and retry validation hook.

Build locally with `docker build -t zepto-assistant .`, then `docker run -p 7860:7860 zepto-assistant`.
