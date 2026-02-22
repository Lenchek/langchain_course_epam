"""RAG evaluation (same as stage_3)."""
import time
from typing import List
from langchain.schema import Document


def measure_latency_single(invoke_fn, query: str, rounds: int = 3) -> dict:
    times = []
    for _ in range(rounds):
        start = time.perf_counter()
        invoke_fn(query)
        times.append(time.perf_counter() - start)
    return {"avg_seconds": sum(times) / len(times), "min_seconds": min(times), "max_seconds": max(times), "rounds": rounds}


def _doc_is_relevant(doc: Document, relevant_sources: List[str], content_marker: str = None) -> bool:
    if relevant_sources and doc.metadata.get("source") in relevant_sources:
        return True
    if content_marker and content_marker.lower() in (doc.page_content or "").lower():
        return True
    return False


def evaluate_retrieval(vector_store, test_cases: List[dict], k: int = 3) -> dict:
    results = []
    for case in test_cases:
        query = case["query"]
        relevant_sources = case.get("relevant_sources") or case.get("relevant_source")
        if isinstance(relevant_sources, str):
            relevant_sources = [relevant_sources]
        content_marker = case.get("content_marker")
        docs = vector_store.similarity_search(query, k=k)
        retrieved_relevant = sum(1 for d in docs if _doc_is_relevant(d, relevant_sources or [], content_marker))
        total_relevant = len(relevant_sources) if relevant_sources else 1
        recall = retrieved_relevant / total_relevant if total_relevant else (1.0 if retrieved_relevant else 0.0)
        precision = retrieved_relevant / k if k else 0.0
        results.append({"query": query, "recall_at_k": recall, "precision_at_k": precision, "retrieved_relevant": retrieved_relevant})
    return {
        "k": k,
        "avg_recall": sum(r["recall_at_k"] for r in results) / len(results) if results else 0,
        "avg_precision": sum(r["precision_at_k"] for r in results) / len(results) if results else 0,
        "cases": results,
    }
