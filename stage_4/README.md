# Stage 4: Orchestrating All Components via LangGraph

Stage 4 wires the full pipeline (RAG chatbot, human-in-the-loop admin, MCP-style data recording) into a **LangGraph** workflow so all components are orchestrated in one place.

## Graph structure

- **user_interaction** — RAG + submit reservation + status (context of RAG and chatbot).
- **admin_approval** — Placeholder node; real approval is done in `run_admin.py`.
- **data_recording** — Writes confirmed reservation to file (Name | Car Number | Reservation Period | Approval Time).

Flow: `START` → (if `record_requested` and `reservation_data`) **data_recording** → END; else **user_interaction** → END.  
User messages go through **user_interaction**. When the admin approves in `run_admin.py`, the code calls `notify_confirmed_reservation` (same as stage_3); the graph’s **data_recording** node is used when you invoke the pipeline with `reservation_data` and `record_requested` (e.g. for tests).

## Setup

Dependencies are pinned to avoid conflicts: **pydantic v1** (langchain and langchainplus-sdk require it), **langchain-core 0.1.x**, **langgraph 0.0.35**. Use the **constraints** file so pip doesn’t upgrade to pydantic 2:

```bash
cd stage_4
python -m venv .venv
.venv\Scripts\activate
pip install -c constraints.txt -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY (and ACTIVELOOP_* if needed)
python ingest.py
```

**If you already see "pydantic 2.12.5 which is incompatible":** downgrade pydantic, then reinstall:

```bash
pip install "pydantic>=1.10,<2"
pip install -c constraints.txt -r requirements.txt
```

## Run

1. **Chatbot (direct, same as stage_3):**
   ```bash
   python run_chatbot.py
   ```

2. **Orchestrated (each user turn through LangGraph):**
   ```bash
   python run_orchestrated.py
   ```

3. **Administrator:**
   ```bash
   python run_admin.py
   ```
   On approve, the reservation is written to the confirmed file (and optionally to the server if `RESERVATION_SERVER_URL` is set).

4. **Optional reservation writer server:**
   ```bash
   python run_server.py
   ```

5. **Evaluation:**
   ```bash
   python run_evaluate.py
   ```

## Architecture

- **First agent:** RAG chatbot (vector store + SQLite dynamic data); collects reservation and answers status.
- **Second agent:** LangChain agent that formats requests for the admin; approval is done in `run_admin.py`.
- **MCP-style server:** FastAPI `POST /confirmed` writes to file; or use the function-call fallback (no server).
- **LangGraph:** `graph.py` defines the pipeline; `run_user_turn()` runs the user_interaction path; `run_record_reservation()` runs the data_recording path.

## Documentation

- **Setup:** above; `.env` in stage_4.
- **Deployment:** run from stage_4; ensure `OPENAI_API_KEY` and (for cloud) `ACTIVELOOP_TOKEN` are set; server is optional and can be behind a reverse proxy with API key.
