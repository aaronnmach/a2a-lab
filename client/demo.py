"""End-to-end demo for the Echo A2A agent."""

from __future__ import annotations

import os

from client import A2AClient


def main() -> None:
    agent_url = os.getenv(
        "A2A_AGENT_URL",
        "https://echo-a2a-agent-ijybv5o3zq-uc.a.run.app",
    )

    with A2AClient(agent_url) as client:
        card = client.fetch_agent_card()
        print(f"Agent: {card['name']} ({card['version']})")
        print("Skills:")
        for skill in client.get_skills():
            print(f"- {skill['name']}: {skill['description']}")

        response = client.send_task("Hello from the client!")
        print("Response text:", client.extract_text(response))


if __name__ == "__main__":
    main()
