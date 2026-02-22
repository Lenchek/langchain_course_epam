"""Second agent (LangChain): interacts with the administrator for reservation approval.

- Generates and formats reservation confirmation requests for the admin.
- Can parse admin reply text into approved/refused (optional).
"""
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

from config import OPENAI_MODEL


def format_reservation_request_for_admin(request: dict) -> str:
    """Generate a human-readable reservation request message for the administrator (second agent)."""
    prompt = PromptTemplate(
        input_variables=["name", "surname", "car_number", "period_start", "period_end", "request_id", "created_at"],
        template="""Format the following parking reservation request for the administrator to review.

Request ID: {request_id}
Submitted at: {created_at}

Customer: {name} {surname}
Car registration: {car_number}
Period: from {period_start} to {period_end}

Write a short, clear summary (2-3 lines) for the admin to approve or refuse.""",
    )
    llm = OpenAI(model=OPENAI_MODEL, temperature=0)
    return llm.predict(
        prompt.format(
            request_id=request["id"],
            created_at=request.get("created_at", ""),
            name=request["name"],
            surname=request["surname"],
            car_number=request["car_number"],
            period_start=request["period_start"],
            period_end=request["period_end"],
        )
    )


def parse_admin_response(admin_reply: str) -> str:
    """Parse admin reply text into 'approved' or 'refused'. Uses LLM for flexibility."""
    if not admin_reply or not admin_reply.strip():
        return "refused"
    prompt = PromptTemplate(
        input_variables=["reply"],
        template="""The administrator replied to a reservation request with this message:
"{reply}"

Respond with exactly one word: approved or refused.""",
    )
    llm = OpenAI(model=OPENAI_MODEL, temperature=0)
    out = llm.predict(prompt.format(reply=admin_reply)).strip().lower()
    if "approv" in out:
        return "approved"
    return "refused"
