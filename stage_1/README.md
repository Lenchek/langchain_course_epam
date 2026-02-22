# Stage 1: RAG Chatbot for Parking Reservation

Self-contained Stage 1 of the parking reservation chatbot: RAG over static data (Activeloop), dynamic data in SQLite, guardrails, and evaluation.

## Requirements

- Python 3.10+
- **OpenAI API key** (for embeddings and chat)
- **Activeloop account** (for vector DB; token for cloud datasets)

## SQLite vs Docker for SQL

This stage uses **SQLite** so you can run everything from this folder with no extra services:

- Single file `data/parking.db`, no Docker or network
- Same SQL interface; you can switch to PostgreSQL in later stages (e.g. Docker) if needed

## Setup (run from `stage_1` folder)

```bash
cd stage_1
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```


Edit `.env`:

- `OPENAI_API_KEY=sk-...`
- `ACTIVELOOP_TOKEN=...` (get from [app.activeloop.ai](https://app.activeloop.ai))
- `ACTIVELOOP_DATASET_PATH=hub://YOUR_USERNAME/parking-stage1` (cloud)  
  Or use a local path: `ACTIVELOOP_DATASET_PATH=./data/deeplake_parking`

## Data

- **Static data** (general info, location, booking process, policies): generated in `data_gen.py`, ingested into Activeloop.
- **Dynamic data** (working hours, prices, availability): generated and stored in SQLite in `data/parking.db`.

Run ingest once:

```bash
python ingest.py
```

This creates/overwrites the vector dataset and seeds SQLite.

## Run chatbot

```bash
python run_chatbot.py
```

Ask about location, hours, prices, availability, or start a reservation (name, surname, car number, period). Reservation confirmation is handled in Stage 2.

## Guardrails

- **Regex-based** PII detection (no Presidio, to keep Pydantic v1 for LangChain): emails, phones, card-like and SSN-like numbers. Use `redact_sensitive(text)` before logging or storing user input; optional for display.

## Evaluation

```bash
python run_evaluate.py
```

- **Latency**: average response time (seconds) over a few queries.
- **Retrieval**: Recall@K and Precision@K for sample queries vs expected document sources.

## Layout

```
stage_1/
  config.py         # Env and paths
  data_gen.py       # Generated static docs + dynamic fixture
  db.py             # SQLite schema and helpers
  vector_store.py   # Activeloop Deep Lake build/load
  guardrails.py     # PII detection and redaction
  chatbot.py        # RAG chain + dynamic context
  evaluate.py       # Latency and Recall/Precision
  ingest.py         # One-time: vector store + SQLite seed
  run_chatbot.py    # Interactive chat
  run_evaluate.py   # Run evaluation
  requirements.txt
  .env.example
  README.md
  data/             # Created on first run (SQLite DB, optional local Deep Lake)
```

## Optional

- Use **local** Deep Lake path (`./data/deeplake_parking`) to avoid Activeloop cloud and token.
- For production or Stage 4, you can replace SQLite with PostgreSQL (e.g. Docker) by changing `db.py` and connection string in config.
