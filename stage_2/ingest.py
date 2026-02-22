"""Ingest static data into Activeloop and seed SQLite. Run once from stage_2 folder."""
import os
import sys

from db import init_db
from vector_store import build_vector_store
from dotenv import load_dotenv

load_dotenv(override=True)


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in .env or environment.")
        sys.exit(1)
    if "hub://" in os.getenv("ACTIVELOOP_DATASET_PATH", "") and not os.getenv("ACTIVELOOP_TOKEN"):
        print("For Activeloop cloud (hub://), set ACTIVELOOP_TOKEN.")
        sys.exit(1)

    print("Initializing SQLite (dynamic data + reservation_requests)...")
    init_db()
    print("Building vector store (Activeloop)...")
    build_vector_store(overwrite=True)
    print("Done. Run: python run_chatbot.py  and  python run_admin.py (for administrator).")


if __name__ == "__main__":
    main()
