# LangChain Course — EPAM Parking Reservation Chatbot

A step-by-step chatbot project: from RAG and guardrails to human-in-the-loop approval and LangGraph orchestration. Each **stage** builds on the previous one; you can run any stage independently.

---

## Course stages

| Stage | What you build | README |
|-------|----------------|--------|
| **1** | **RAG chatbot** — static + dynamic data, guardrails, evaluation | [→ Stage 1](stage_1/README.md) |
| **2** | **Human-in-the-loop** — second agent, admin approve/refuse, reservation status | [→ Stage 2](stage_2/README.md) |
| **3** | **Confirmed reservations** — MCP-style server or direct writer, file output | [→ Stage 3](stage_3/README.md) |
| **4** | **LangGraph orchestration** — full pipeline in one graph (user interaction + data recording) | [→ Stage 4](stage_4/README.md) |

---

## Quick navigation

- **[Stage 1: RAG Chatbot for Parking Reservation](stage_1/README.md)** — RAG over Activeloop + SQLite, guardrails, eval.
- **[Stage 2: Human-in-the-Loop Agent](stage_2/README.md)** — Escalation to admin; approve/refuse; status by ID.
- **[Stage 3: Process Confirmed Reservations (MCP-Style Server)](stage_3/README.md)** — Write approved reservations to file (FastAPI server or direct call).
- **[Stage 4: Orchestrating All Components via LangGraph](stage_4/README.md)** — Single LangGraph pipeline; setup and dependency notes.

---

## How to use

1. Pick a stage (1–4) and open its README via the links above.
2. Follow that stage’s **Setup** (venv, `pip install`, `.env`, `ingest.py` if needed).
3. Run the scripts listed in that stage’s **Run** section.

Stages are self-contained: each has its own `requirements.txt` and instructions. For Stage 4, use a dedicated venv and the provided `constraints.txt` to avoid dependency conflicts.
