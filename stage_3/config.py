"""Stage 3 configuration from environment."""
import os
from pathlib import Path

from dotenv import load_dotenv

STAGE_DIR = Path(__file__).resolve().parent
load_dotenv(STAGE_DIR / ".env")

DATA_DIR = STAGE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

ACTIVELOOP_DATASET_PATH = os.getenv(
    "ACTIVELOOP_DATASET_PATH",
    str(DATA_DIR / "deeplake_parking"),
)
ACTIVELOOP_TOKEN = os.getenv("ACTIVELOOP_TOKEN", "")

SQLITE_PATH = os.getenv("SQLITE_PATH", str(DATA_DIR / "parking.db"))

# Stage 3: confirmed reservations file (Name | Car Number | Reservation Period | Approval Time)
CONFIRMED_RESERVATIONS_FILE = os.getenv(
    "CONFIRMED_RESERVATIONS_FILE",
    str(DATA_DIR / "confirmed_reservations.txt"),
)
# Optional: reservation writer server URL (if set, run_admin POSTs here on approve)
RESERVATION_SERVER_URL = os.getenv("RESERVATION_SERVER_URL", "")
RESERVATION_SERVER_API_KEY = os.getenv("RESERVATION_SERVER_API_KEY", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
