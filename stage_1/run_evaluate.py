"""Run RAG evaluation: latency and retrieval metrics. Run from stage_1: python run_evaluate.py"""
import sys

from config import OPENAI_API_KEY
from vector_store import get_vector_store
from chatbot import build_rag_chain, get_reply
from evaluate import measure_latency_single, evaluate_retrieval


def main():
    if not OPENAI_API_KEY:
        print("Set OPENAI_API_KEY in .env or environment.")
        sys.exit(1)

    print("Loading vector store...")
    vs = get_vector_store()
    print("Building RAG chain (RetrievalQA.from_llm + retriever)...")
    chain = build_rag_chain()

    # Latency: same interface as run_chatbot (get_reply(chain, query) -> chain.run(query=...))
    print("\n--- Latency (3 rounds) ---")
    latency = measure_latency_single(
        lambda q: get_reply(chain, q),
        "What are the working hours?",
        rounds=3,
    )
    print(f"Avg: {latency['avg_seconds']:.3f}s, Min: {latency['min_seconds']:.3f}s, Max: {latency['max_seconds']:.3f}s")

    # Retrieval quality: by metadata["source"] when present; fallback to content_marker
    test_cases = [
        {"query": "Where is the parking located?", "relevant_sources": ["location"], "content_marker": "123 Main Street"},
        {"query": "How do I book a space?", "relevant_sources": ["booking"], "content_marker": "Reservations are subject"},
        {"query": "What are the prices?", "relevant_sources": ["general"], "content_marker": "450 parking spaces"},
        {"query": "Cancellation policy?", "relevant_sources": ["policies"], "content_marker": "Free cancellation"},
    ]
    print("\n--- Retrieval (Recall@K, Precision@K, K=3) ---")
    ret = evaluate_retrieval(vs, test_cases, k=3)
    print(f"Avg Recall@3: {ret['avg_recall']:.3f}")
    print(f"Avg Precision@3: {ret['avg_precision']:.3f}")
    for c in ret["cases"]:
        q_short = c["query"][:50] + "..." if len(c["query"]) > 50 else c["query"]
        print(f"  Q: {q_short} -> R@{ret['k']}={c['recall_at_k']:.2f}, P@{ret['k']}={c['precision_at_k']:.2f}")

    print("\nEvaluation done.")


if __name__ == "__main__":
    main()
