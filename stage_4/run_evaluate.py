"""Run RAG evaluation. Run from stage_4: python run_evaluate.py"""
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)
from dotenv import load_dotenv
load_dotenv(override=True)

import os
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
    latency = measure_latency_single(lambda q: get_reply(chain, q), "What are the working hours?", rounds=3)
    print(f"Latency: avg={latency['avg_seconds']:.3f}s")
    test_cases = [
        {"query": "Where is the parking located?", "relevant_sources": ["location"], "content_marker": "123 Main Street"},
        {"query": "How do I book?", "relevant_sources": ["booking"], "content_marker": "Reservations are subject"},
    ]
    ret = evaluate_retrieval(vs, test_cases, k=3)
    print(f"Avg Recall@3: {ret['avg_recall']:.3f}, Precision@3: {ret['avg_precision']:.3f}")
    print("Done.")


if __name__ == "__main__":
    main()
