"""FastAPI server: POST /confirmed writes to file (MCP-style)."""
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel

from config import RESERVATION_SERVER_API_KEY, CONFIRMED_RESERVATIONS_FILE
from reservation_writer import write_confirmed_reservation

app = FastAPI(title="Reservation Writer", description="Stage 4: process confirmed reservations to file")


class ConfirmedBody(BaseModel):
    name: str
    surname: str
    car_number: str
    period_start: str
    period_end: str
    approval_time: Optional[str] = None


def require_api_key(x_api_key: Optional[str] = Header(None)):
    if not RESERVATION_SERVER_API_KEY:
        return
    if x_api_key != RESERVATION_SERVER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


@app.post("/confirmed")
def post_confirmed(body: ConfirmedBody, _: str = Depends(require_api_key)):
    approval_time = body.approval_time or datetime.utcnow().isoformat()
    path = write_confirmed_reservation(
        name=body.name,
        surname=body.surname,
        car_number=body.car_number,
        period_start=body.period_start,
        period_end=body.period_end,
        approval_time=approval_time,
    )
    return {"status": "written", "file": path}


@app.get("/health")
def health():
    return {"status": "ok", "file": CONFIRMED_RESERVATIONS_FILE}
