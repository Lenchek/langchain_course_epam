"""Interactive chatbot (Stage 3: same as stage_2)."""
import os
import sys
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)
from dotenv import load_dotenv
load_dotenv(override=True)

from chatbot import build_rag_chain, get_reply, try_submit_reservation, answer_reservation_status
from guardrails import redact_sensitive


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in .env or environment.")
        sys.exit(1)

    chain = build_rag_chain()
    print("Central Garage parking assistant (Stage 3: with admin approval + confirmed reservations file).")
    print("Ask about location, hours, prices; or provide reservation details to submit.")
    print("Example: 'I want to book: John Doe, Doe, AB-1234, 2025-02-22 09:00 to 2025-02-22 17:00'")
    print("Type 'quit' or 'exit' to end.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        status_reply = answer_reservation_status(user_input)
        if status_reply is not None:
            print("Assistant:", status_reply)
            print()
            continue

        submitted, submit_reply = try_submit_reservation(user_input)
        if submitted:
            print("Assistant:", submit_reply)
            print()
            continue

        _ = redact_sensitive(user_input)
        reply = get_reply(chain, user_input)
        print("Assistant:", reply)
        print()

    print("Goodbye.")


if __name__ == "__main__":
    main()
