"""RAG chatbot: answer questions and collect reservation data."""
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.schema import BaseRetriever, Document

from config import OPENAI_MODEL
from db import get_working_hours, get_prices, get_availability_summary
from vector_store import get_vector_store
from datetime import date


def get_dynamic_context() -> str:
    """Format dynamic data from SQLite for the LLM context."""
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
    """Wraps a retriever and prepends a document with dynamic context (hours, prices, availability)."""

    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever

    def get_relevant_documents(self, query: str):
        dynamic_doc = Document(page_content=get_dynamic_context(), metadata={"source": "dynamic"})
        docs = self.retriever.get_relevant_documents(query)
        return [dynamic_doc] + docs

    async def aget_relevant_documents(self, query: str):
        dynamic_doc = Document(page_content=get_dynamic_context(), metadata={"source": "dynamic"})
        docs = await self.retriever.aget_relevant_documents(query)
        return [dynamic_doc] + docs


def build_rag_chain():
    """Build RAG chain using this package's RetrievalQA API (from_llm + combine_documents_chain)."""
    llm = OpenAI(model=OPENAI_MODEL, temperature=0)
    vectorstore = get_vector_store()
    base_retriever = vectorstore.as_retriever()
    retriever = RetrieverWithDynamicContext(retriever=base_retriever)

    # Prompt must use only "context" and "question" (required by StuffDocumentsChain in this LangChain version)
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a helpful assistant for "Central Garage" parking. Use ONLY the following context to answer.
If the user wants to make a reservation, collect: full name, surname, car registration number, and reservation period (start and end date/time).
Do not invent information. If something is not in the context, say you don't have that information.

Context:
{context}

Question: {question}
Helpful Answer:""",
    )

    return RetrievalQA.from_llm(llm=llm, prompt=prompt, retriever=retriever)


def get_reply(rag, user_message: str) -> str:
    """Get one RAG reply. This package's RetrievalQA uses input key 'query'."""
    return rag.run(query=user_message)


# Reservation slot: we only collect in Stage 1; confirmation is Stage 2
RESERVATION_FIELDS = ["name", "surname", "car_number", "period_start", "period_end"]


def parse_reservation_intent(text: str) -> dict:
    """Naive extraction: look for key phrases. In production use a dedicated NER or tool."""
    collected = {}
    text_lower = text.lower()
    # Could add regex or a small LLM call to extract structured fields
    if "reserv" in text_lower or "book" in text_lower:
        collected["intent"] = "reservation"
    return collected
