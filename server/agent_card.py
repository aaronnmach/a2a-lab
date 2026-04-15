"""Agent Card definition and validation helpers for the A2A lab."""

from __future__ import annotations

from typing import Any


AGENT_CARD: dict[str, Any] = {
    "id": "echo-agent-v1",
    "name": "Echo Agent",
    "version": "1.0.0",
    "description": "A simple agent that echoes back text or returns a mock summary.",
    "url": "https://echo-a2a-agent-ijybv5o3zq-uc.a.run.app",
    "contact": {
        "email": "student@example.com",
    },
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "id": "echo",
            "name": "Echo",
            "description": "Returns the user message verbatim.",
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        },
        {
            "id": "summarise",
            "name": "Summarise",
            "description": "Returns a one-sentence mock summary when the input starts with !summarise.",
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        },
    ],
}


REQUIRED_TOP_LEVEL_FIELDS = {
    "id",
    "name",
    "version",
    "description",
    "url",
    "contact",
    "capabilities",
    "defaultInputModes",
    "defaultOutputModes",
    "skills",
}

REQUIRED_CONTACT_FIELDS = {"email"}
REQUIRED_CAPABILITY_FIELDS = {"streaming", "pushNotifications"}
REQUIRED_SKILL_FIELDS = {"id", "name", "description", "inputModes", "outputModes"}


def validate_card(card: dict) -> bool:
    """Return True when the supplied Agent Card contains the required fields.

    This validation intentionally stays lightweight for the lab: it checks that
    the expected top-level keys exist, that the contact and capabilities objects
    contain their required keys, and that every declared skill contains the
    required skill metadata. It returns False for missing or malformed sections.
    """

    if not isinstance(card, dict):
        return False

    if not REQUIRED_TOP_LEVEL_FIELDS.issubset(card.keys()):
        return False

    contact = card.get("contact")
    if not isinstance(contact, dict) or not REQUIRED_CONTACT_FIELDS.issubset(contact.keys()):
        return False

    capabilities = card.get("capabilities")
    if not isinstance(capabilities, dict) or not REQUIRED_CAPABILITY_FIELDS.issubset(capabilities.keys()):
        return False

    skills = card.get("skills")
    if not isinstance(skills, list) or not skills:
        return False

    for skill in skills:
        if not isinstance(skill, dict) or not REQUIRED_SKILL_FIELDS.issubset(skill.keys()):
            return False

    return True
