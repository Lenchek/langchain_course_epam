"""Stage 4: LangGraph orchestration of user interaction, admin approval, and data recording.

Graph structure:
- user_interaction: RAG chatbot + submit reservation + status (context of RAG and chatbot).
- data_recording: write confirmed reservation to file (MCP server / function call).
Admin approval is done in run_admin.py (outside the graph), not as a graph node.
"""
from typing import TypedDict, Optional, Literal

# LangGraph 0.0.35 API: no START; use set_conditional_entry_point
from langgraph.graph import StateGraph, END

from chatbot import (
    build_rag_chain,
    get_reply,
    try_submit_reservation,
    answer_reservation_status,
)
from reservation_writer import notify_confirmed_reservation


class PipelineState(TypedDict, total=False):
    user_input: str
    reply: str
    reservation_id: Optional[int]
    reservation_data: Optional[dict]
    record_requested: bool
    recorded: bool
    next_node: Optional[str]


def user_interaction(state: PipelineState) -> PipelineState:
    """Node: RAG + submit + status. Returns reply and optional reservation_id."""
    user_input = (state.get("user_input") or "").strip()
    if not user_input:
        return {"reply": "Please enter a message."}

    status_reply = answer_reservation_status(user_input)
    if status_reply is not None:
        return {"reply": status_reply}

    submitted, submit_reply = try_submit_reservation(user_input)
    if submitted:
        return {"reply": submit_reply}

    rag = build_rag_chain()
    reply = get_reply(rag, user_input)
    return {"reply": reply}


def data_recording(state: PipelineState) -> PipelineState:
    """Node: write confirmed reservation to file (Name | Car Number | Reservation Period | Approval Time)."""
    data = state.get("reservation_data")
    if not data or not state.get("record_requested"):
        return {"recorded": False}
    approval_time = data.get("approval_time") or ""
    notify_confirmed_reservation(
        req={
            "name": data.get("name", ""),
            "surname": data.get("surname", ""),
            "car_number": data.get("car_number", ""),
            "period_start": data.get("period_start", ""),
            "period_end": data.get("period_end", ""),
        },
        approval_time=approval_time,
    )
    return {"recorded": True}


def route_after_start(state: PipelineState) -> Literal["user_interaction", "data_recording"]:
    """If we have reservation_data and record_requested, go to data_recording; else user_interaction."""
    if state.get("record_requested") and state.get("reservation_data"):
        return "data_recording"
    return "user_interaction"


def build_pipeline():
    """Build and compile the LangGraph pipeline (LangGraph 0.0.35 API)."""
    graph = StateGraph(PipelineState)

    graph.add_node("user_interaction", user_interaction)
    graph.add_node("data_recording", data_recording)

    graph.set_conditional_entry_point(
        route_after_start,
        {"user_interaction": "user_interaction", "data_recording": "data_recording"},
    )
    graph.add_edge("user_interaction", END)
    graph.add_edge("data_recording", END)

    return graph.compile()


def run_user_turn(user_input: str) -> str:
    """Run one user turn through the pipeline. Returns assistant reply."""
    pipeline = build_pipeline()
    result = pipeline.invoke({"user_input": user_input})
    return result.get("reply", "")


def run_record_reservation(reservation_data: dict, approval_time: str) -> bool:
    """Run data_recording node for an approved reservation. Returns True if written."""
    data = {**reservation_data, "approval_time": approval_time}
    pipeline = build_pipeline()
    result = pipeline.invoke({"reservation_data": data, "record_requested": True})
    return result.get("recorded", False)
