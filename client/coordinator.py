"""Bonus coordinator that chains EchoAgent and ReverseAgent via A2A."""

from __future__ import annotations

import os

from client import A2AClient


def main() -> None:
    echo_url = os.getenv("ECHO_AGENT_URL", "http://localhost:8000")
    reverse_url = os.getenv("REVERSE_AGENT_URL", "http://localhost:8001")

    with A2AClient(echo_url) as echo_client, A2AClient(reverse_url) as reverse_client:
        echo_client.fetch_agent_card()
        reverse_client.fetch_agent_card()

        original = "Hello from the chained multi agent demo"
        echo_result = echo_client.extract_text(echo_client.send_task(original))
        reverse_result = reverse_client.extract_text(reverse_client.send_task(echo_result))

        print("Original:", original)
        print("Echo output:", echo_result)
        print("Reverse output:", reverse_result)


if __name__ == "__main__":
    main()
