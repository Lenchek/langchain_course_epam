# Stage 3: Process Confirmed Reservations (MCP-Style Server)

Stage 3 adds a **reservation writer** so that when the administrator approves a reservation, the details are written to a text file. You can use either a **FastAPI server** (MCP-style) or a **direct function call** (tool/function call fallback).

## What’s added

- **File format:** `Name | Car Number | Reservation Period | Approval Time` (one line per approved reservation).
- **reservation_writer.py:** `write_confirmed_reservation(...)` appends one line to the file; `notify_confirmed_reservation(req, approval_time)` either POSTs to the server (if `RESERVATION_SERVER_URL` is set) or calls the writer directly.
- **server.py:** FastAPI app with `POST /confirmed` (JSON body: name, surname, car_number, period_start, period_end, approval_time). Optional `X-API-Key` for security.
- **run_admin.py:** On approve, calls `notify_confirmed_reservation(req, approval_time)` so the reservation is written (via server or file).
- **run_server.py:** Starts the FastAPI server (e.g. `http://127.0.0.1:8000`).

## Setup

```bash
cd stage_3
pip install -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY (and ACTIVELOOP_* if needed)
python ingest.py
```

## Run

1. **Without server (simplest):**  
   Leave `RESERVATION_SERVER_URL` empty. When the admin approves, the script writes directly to `data/confirmed_reservations.txt`.

   ```bash
   python run_chatbot.py   # user
   python run_admin.py     # admin: approve → file written
   ```

2. **With server:**  
   In one terminal:
   ```bash
   python run_server.py
   ```
   In `.env` set:
   ```bash
   RESERVATION_SERVER_URL=http://127.0.0.1:8000
   RESERVATION_SERVER_API_KEY=your-secret   # optional
   ```
   Then run `run_admin.py`; on approve it POSTs to the server, which appends to the file.

## Security

- Server: set `RESERVATION_SERVER_API_KEY` in `.env`; clients must send `X-API-Key: <value>`.
- Run the server on localhost or behind a reverse proxy; avoid exposing it publicly without auth.

## Layout

- `config.py` — adds `CONFIRMED_RESERVATIONS_FILE`, `RESERVATION_SERVER_URL`, `RESERVATION_SERVER_API_KEY`.
- `reservation_writer.py` — file write + `notify_confirmed_reservation` (server or direct).
- `server.py` — FastAPI app, `POST /confirmed`, `GET /health`.
- `run_server.py` — uvicorn entrypoint.
- Rest as in stage_2 (db, chatbot, admin_agent, run_chatbot, run_admin, ingest, evaluate).
