"""Ingest static data and seed SQLite. Run once from stage_4 folder."""
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import sys
from db import init_db
from vector_store import build_vector_store


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in .env or environment.")
        sys.exit(1)
    if "hub://" in os.getenv("ACTIVELOOP_DATASET_PATH", "") and not os.getenv("ACTIVELOOP_TOKEN"):
        print("For Activeloop cloud (hub://), set ACTIVELOOP_TOKEN.")
        sys.exit(1)

    print("Initializing SQLite...")
    init_db()
    print("Building vector store...")
    build_vector_store(overwrite=True)
    print("Done. Run: python run_chatbot.py, python run_admin.py, python run_orchestrated.py, optionally python run_server.py")


if __name__ == "__main__":
    main()
