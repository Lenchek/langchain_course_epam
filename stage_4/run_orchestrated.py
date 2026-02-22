"""Orchestrated pipeline via LangGraph: user turns go through the graph (Stage 4)."""
from serbia_ssl_patch import _patched_create_default_context
print("SSL certs are patched:", _patched_create_default_context)
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import sys
from graph import run_user_turn


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in .env or environment.")
        sys.exit(1)

    print("Central Garage (Stage 4: LangGraph orchestration). Each message goes through the pipeline.")
    print("Ask about location, hours, prices; or submit a reservation. Type 'quit' or 'exit' to end.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        reply = run_user_turn(user_input)
        print("Assistant:", reply)
        print()

    print("Goodbye.")


if __name__ == "__main__":
    main()
