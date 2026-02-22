"""Start the reservation writer server (FastAPI). Run from stage_3: python run_server.py"""
import os
import uvicorn
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)
from dotenv import load_dotenv
load_dotenv(override=True)

from server import app

if __name__ == "__main__":
    
    host = os.getenv("RESERVATION_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("RESERVATION_SERVER_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
