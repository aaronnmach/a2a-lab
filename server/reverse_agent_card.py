"""Agent Card for the optional ReverseAgent bonus."""

from __future__ import annotations

from typing import Any

REVERSE_AGENT_CARD: dict[str, Any] = {
    "id": "reverse-agent-v1",
    "name": "Reverse Agent",
    "version": "1.0.0",
    "description": "An agent that returns the input words in reverse order.",
    "url": "http://localhost:8001",
    "contact": {"email": "student@example.com"},
    "capabilities": {"streaming": False, "pushNotifications": False},
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "id": "reverse-words",
            "name": "Reverse Words",
            "description": "Reverses the order of words in the user's message.",
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        }
    ],
}
