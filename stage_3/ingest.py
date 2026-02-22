"""Ingest static data and seed SQLite. Run once from stage_3 folder."""
import os
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
import serbia_ssl_patch  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

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
    print("Done. Run: python run_chatbot.py, python run_admin.py, optionally python run_server.py")


if __name__ == "__main__":
    main()
