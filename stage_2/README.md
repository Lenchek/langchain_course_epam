# Stage 2: Human-in-the-Loop Agent

Stage 2 extends Stage 1 with a **second agent** that interacts with the administrator: reservation requests are escalated to a human for approve/refuse.

## What’s added

- **First agent (unchanged):** RAG chatbot — answers questions and collects reservation details.
- **Escalation:** When the user provides name, surname, car number, and period, the chatbot creates a **reservation request** and tells the user it was sent to the administrator (request ID).
- **Second agent:** LangChain agent that formats reservation requests for the admin and (optionally) parses admin replies.
- **Administrator flow:** Run `run_admin.py` to list pending requests and approve or refuse each one (stored in SQLite).
- **Status:** User can ask “What is the status of my reservation &lt;ID&gt;?” and get pending/approved/refused.

## Setup

Same as Stage 1 (from `stage_2` folder):

```bash
cd stage_2
pip install -r requirements.txt
cp .env.example .env
# Edit .env: OPENAI_API_KEY, ACTIVELOOP_* if using cloud
python ingest.py
```

## Run

1. **Chatbot (user side):**
   ```bash
   python run_chatbot.py
   ```
   - Ask about location, hours, prices.
   - Submit a reservation, e.g.:  
     `I want to book: John Doe, Doe, AB-1234, 2025-02-22 09:00 to 2025-02-22 17:00`
   - Then ask: `What is the status of my reservation 1?`

2. **Administrator (approve/refuse):**
   ```bash
   python run_admin.py
   ```
   - Lists pending requests.
   - For each: type `a` to approve, `r` to refuse (optional comment).

## Layout

- `config.py`, `data_gen.py`, `db.py`, `vector_store.py`, `guardrails.py` — same role as Stage 1; `db.py` adds table `reservation_requests`.
- `admin_agent.py` — second agent: formats request for admin, can parse admin reply.
- `chatbot.py` — first agent + `try_submit_reservation`, `answer_reservation_status`.
- `run_chatbot.py` — interactive chat with submit and status.
- `run_admin.py` — admin console: pending list, approve/refuse.
- `ingest.py`, `evaluate.py`, `run_evaluate.py` — as in Stage 1.

## Communication between agents

- **First → second:** The chatbot does not call the admin agent at submit time; it only writes a row in `reservation_requests` (status `pending`). The **administrator** runs `run_admin.py`, which uses the **second agent** to format each pending request for display, then the admin approves/refuses via the console (DB is updated).
- So: “sending to administrator” = persisting the request; the human uses `run_admin.py` to respond; the user checks status via the chatbot.
