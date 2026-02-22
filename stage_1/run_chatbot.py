"""Interactive RAG chatbot. Run from stage_1 folder: python run_chatbot.py"""
import os
import sys
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)

from chatbot import build_rag_chain, get_reply
from guardrails import redact_sensitive


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in .env or environment.")
        sys.exit(1)

    chain = build_rag_chain()
    print("Central Garage parking assistant. Ask about location, hours, prices, or make a reservation.")
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

        # Optional: redact user input for logging (guardrails)
        safe_log = redact_sensitive(user_input)
        reply = get_reply(chain, user_input)
        print("Assistant:", reply)
        print()

    print("Goodbye.")


if __name__ == "__main__":
    main()
