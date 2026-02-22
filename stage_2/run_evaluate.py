"""Run RAG evaluation. Run from stage_2: python run_evaluate.py"""
import sys

from config import OPENAI_API_KEY
from vector_store import get_vector_store
from chatbot import build_rag_chain, get_reply
from evaluate import measure_latency_single, evaluate_retrieval


def main():
    if not OPENAI_API_KEY:
        print("Set OPENAI_API_KEY in .env or environment.")
        sys.exit(1)

    vs = get_vector_store()
    chain = build_rag_chain()
    print("--- Latency (3 rounds) ---")
    latency = measure_latency_single(lambda q: get_reply(chain, q), "What are the working hours?", rounds=3)
    print(f"Avg: {latency['avg_seconds']:.3f}s, Min: {latency['min_seconds']:.3f}s, Max: {latency['max_seconds']:.3f}s")

    test_cases = [
        {"query": "Where is the parking located?", "relevant_sources": ["location"], "content_marker": "123 Main Street"},
        {"query": "How do I book a space?", "relevant_sources": ["booking"], "content_marker": "Reservations are subject"},
        {"query": "What are the prices?", "relevant_sources": ["general"], "content_marker": "450 parking spaces"},
        {"query": "Cancellation policy?", "relevant_sources": ["policies"], "content_marker": "Free cancellation"},
    ]
    print("\n--- Retrieval (Recall@3, Precision@3) ---")
    ret = evaluate_retrieval(vs, test_cases, k=3)
    print(f"Avg Recall@3: {ret['avg_recall']:.3f}, Avg Precision@3: {ret['avg_precision']:.3f}")
    for c in ret["cases"]:
        q_short = c["query"][:50] + "..." if len(c["query"]) > 50 else c["query"]
        print(f"  {q_short} -> R@3={c['recall_at_k']:.2f}, P@3={c['precision_at_k']:.2f}")
    print("Done.")


if __name__ == "__main__":
    main()
