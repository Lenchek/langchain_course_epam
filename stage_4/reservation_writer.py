"""Write confirmed reservations to file. Format: Name | Car Number | Reservation Period | Approval Time."""
from pathlib import Path

from config import (
    CONFIRMED_RESERVATIONS_FILE,
    RESERVATION_SERVER_URL,
    RESERVATION_SERVER_API_KEY,
)


def write_confirmed_reservation(
    name: str,
    surname: str,
    car_number: str,
    period_start: str,
    period_end: str,
    approval_time: str,
) -> str:
    full_name = f"{name} {surname}".strip()
    reservation_period = f"{period_start} to {period_end}"
    line = f"{full_name} | {car_number} | {reservation_period} | {approval_time}\n"
    path = Path(CONFIRMED_RESERVATIONS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
    return str(path)


def notify_confirmed_reservation(req: dict, approval_time: str) -> None:
    if RESERVATION_SERVER_URL:
        try:
            import urllib.request
            import json
            data = json.dumps({
                "name": req["name"],
                "surname": req["surname"],
                "car_number": req["car_number"],
                "period_start": req["period_start"],
                "period_end": req["period_end"],
                "approval_time": approval_time,
            }).encode("utf-8")
            request = urllib.request.Request(
                f"{RESERVATION_SERVER_URL.rstrip('/')}/confirmed",
                data=data,
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            if RESERVATION_SERVER_API_KEY:
                request.add_header("X-API-Key", RESERVATION_SERVER_API_KEY)
            urllib.request.urlopen(request, timeout=5)
            return
        except Exception:
            pass
    write_confirmed_reservation(
        name=req["name"],
        surname=req["surname"],
        car_number=req["car_number"],
        period_start=req["period_start"],
        period_end=req["period_end"],
        approval_time=approval_time,
    )
