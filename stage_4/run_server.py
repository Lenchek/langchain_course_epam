"""Start the reservation writer server (FastAPI). Run from stage_4: python run_server.py"""
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)
from dotenv import load_dotenv
load_dotenv(override=True)

import os
from server import app


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("RESERVATION_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("RESERVATION_SERVER_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
