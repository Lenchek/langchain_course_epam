"""Stage 1 configuration from environment."""
import os
from pathlib import Path

from dotenv import load_dotenv

STAGE_DIR = Path(__file__).resolve().parent
load_dotenv(override=True)

# Paths: resolve relative to stage_1 folder
DATA_DIR = STAGE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Vector DB (Activeloop Deep Lake)
ACTIVELOOP_DATASET_PATH = os.getenv(
    "ACTIVELOOP_DATASET_PATH",
    str(DATA_DIR / "deeplake_parking"),
)
# Set for Activeloop cloud auth
ACTIVELOOP_TOKEN = os.getenv("ACTIVELOOP_TOKEN", "")

# SQLite for dynamic data
SQLITE_PATH = os.getenv("SQLITE_PATH", str(DATA_DIR / "parking.db"))

# OpenAI (for embeddings + chat)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
