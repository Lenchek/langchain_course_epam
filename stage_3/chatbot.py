"""RAG chatbot (first agent) + escalation to admin (same as stage_2)."""
import re
from typing import Optional
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.schema import BaseRetriever, Document

from config import OPENAI_MODEL
from db import (
    get_working_hours,
    get_prices,
    get_availability_summary,
    create_reservation_request,
    get_reservation_status,
)
from vector_store import get_vector_store
from datetime import date


def get_dynamic_context() -> str:
    lines = ["## Dynamic data (current)\n"]
    try:
        hours = get_working_hours()
        lines.append("Working hours: " + "; ".join(f"{h['day']} {h['open']}-{h['close']}" for h in hours))
    except Exception as e:
        lines.append(f"Error getting working hours: {e}")
    try:
        prices = get_prices()
        lines.append("Prices: " + "; ".join(
            f"{p['type']}: first hour {p['first_hour']} EUR, then {p['next_hours']} EUR/h, day max {p['day_max']} EUR"
            for p in prices
        ))
    except Exception as e:
        lines.append(f"Error getting prices: {e}")
    try:
        today = date.today().isoformat()
        avail = get_availability_summary(today)
        lines.append(f"Availability today ({today}): {avail['available']} of {avail['total']} slots free.")
    except Exception as e:
        lines.append(f"Error getting availability: {e}")
    return "\n".join(lines)


class RetrieverWithDynamicContext(BaseRetriever):
    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever

    def get_relevant_documents(self, query: str):
        dynamic_doc = Document(page_content=get_dynamic_context(), metadata={"source": "dynamic"})
        docs = self.retriever.get_relevant_documents(query)
        return [dynamic_doc] + docs

    async def aget_relevant_documents(self, query: str):
        dynamic_doc = Document(page_content=get_dynamic_context(), metadata={"source": "dynamic"})
        docs = await self.retriever.get_relevant_documents(query)
        return [dynamic_doc] + docs


def build_rag_chain():
    llm = OpenAI(model=OPENAI_MODEL, temperature=0)
    vectorstore = get_vector_store()
    base_retriever = vectorstore.as_retriever()
    retriever = RetrieverWithDynamicContext(retriever=base_retriever)
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a helpful assistant for "Central Garage" parking. Use ONLY the following context to answer.
If the user wants to make a reservation, collect: full name, surname, car registration number, and reservation period (start and end date/time).
After they provide all details, tell them their request will be sent to the administrator for approval.
If the user asks about reservation status, tell them to provide their request ID (a number they received when they submitted).
Do not invent information.

Context:
{context}

Question: {question}
Helpful Answer:""",
    )
    return RetrievalQA.from_llm(llm=llm, prompt=prompt, retriever=retriever)


def get_reply(rag, user_message: str) -> str:
    return rag.run(query=user_message)


RESERVATION_FIELDS = ["name", "surname", "car_number", "period_start", "period_end"]


def extract_reservation_from_text(text: str) -> dict:
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""From the following message, extract parking reservation details if present.
Reply in this exact format, one per line; use empty value if not found:
name: ...
surname: ...
car_number: ...
period_start: ... (date and time, e.g. 2025-02-22 09:00)
period_end: ... (date and time, e.g. 2025-02-22 17:00)

Message:
{text}""",
    )
    llm = OpenAI(model=OPENAI_MODEL, temperature=0)
    raw = llm.predict(prompt.format(text=text))
    result = {}
    for line in raw.strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip().lower().replace(" ", "_")
            val = val.strip()
            if key in RESERVATION_FIELDS and val:
                result[key] = val
    return result


def try_submit_reservation(user_message: str) -> tuple:
    extracted = extract_reservation_from_text(user_message)
    if not all(extracted.get(f) for f in RESERVATION_FIELDS):
        return False, None
    try:
        request_id = create_reservation_request(
            name=extracted["name"],
            surname=extracted["surname"],
            car_number=extracted["car_number"],
            period_start=extracted["period_start"],
            period_end=extracted["period_end"],
        )
        return True, (
            f"Your reservation request has been sent to the administrator. "
            f"Your request ID is {request_id}. You can ask later: 'What is the status of my reservation {request_id}?'"
        )
    except Exception as e:
        return True, f"Sorry, the request could not be submitted: {e}"


def answer_reservation_status(user_message: str) -> Optional[str]:
    match = re.search(r"(?:status|request)\s*(?:of|#|:)?\s*(\d+)|reservation\s*(\d+)|id\s*(\d+)", user_message, re.I)
    request_id_str = (match.group(1) or match.group(2) or match.group(3)) if match else None
    if not request_id_str:
        return None
    try:
        rid = int(request_id_str)
    except ValueError:
        return None
    info = get_reservation_status(rid)
    if not info:
        return f"There is no reservation request with ID {rid}."
    s = info["status"]
    if s == "pending":
        return f"Request {rid} is still pending administrator approval."
    if s == "approved":
        return f"Request {rid} has been approved. Period: {info.get('period_start', '')} to {info.get('period_end', '')}."
    return f"Request {rid} was refused." + (f" Comment: {info['admin_comment']}" if info.get("admin_comment") else "")
