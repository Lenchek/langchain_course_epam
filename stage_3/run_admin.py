"""Administrator console: list pending, approve/refuse. On approve, write to file via server or function (Stage 3)."""
from datetime import datetime
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)
from dotenv import load_dotenv
load_dotenv(override=True)
from db import get_pending_reservation_requests, set_reservation_status
from admin_agent import format_reservation_request_for_admin
from reservation_writer import notify_confirmed_reservation


def main():
    pending = get_pending_reservation_requests()
    if not pending:
        print("No pending reservation requests.")
        return

    print(f"--- {len(pending)} pending request(s) ---\n")
    for req in pending:
        print(f"Request ID: {req['id']}")
        print(f"  {req['name']} {req['surname']} | Car: {req['car_number']}")
        print(f"  Period: {req['period_start']} → {req['period_end']}")
        print(f"  Submitted: {req['created_at']}")
        try:
            summary = format_reservation_request_for_admin(req)
            print(f"  Summary: {summary}")
        except Exception as e:
            print(f"  (Summary unavailable: {e})")
        print()

        while True:
            action = input(f"  [a]pprove / [r]efuse / [s]kip? ").strip().lower()
            if action in ("a", "approve"):
                approval_time = datetime.utcnow().isoformat()
                set_reservation_status(req["id"], "approved")
                try:
                    notify_confirmed_reservation(req, approval_time)
                    print("  → Approved and written to confirmed reservations file.\n")
                except Exception as e:
                    print(f"  → Approved (DB updated). Write to file failed: {e}\n")
                break
            if action in ("r", "refuse"):
                comment = input("  Optional comment: ").strip()
                set_reservation_status(req["id"], "refused", admin_comment=comment)
                print("  → Refused.\n")
                break
            if action in ("s", "skip"):
                print("  Skipped.\n")
                break
            print("  Enter a, r, or s.")

    print("Done.")


if __name__ == "__main__":
    main()
