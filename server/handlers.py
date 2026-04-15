"""Task handling logic for the Echo A2A agent."""

from __future__ import annotations

MOCK_SUMMARY = (
    "Mock summary: the input asks the agent to summarise text, "
    "so this placeholder "
    "returns a single-sentence summary."
)


async def handle_task(request) -> str:
    text_parts = [p.text for p in request.message.parts if p.type == "text"]
    combined = " ".join(text_parts).strip()

    if not combined:
        return ""

    if combined.startswith("!summarise"):
        return "This is a mock one-sentence summary of the provided text."

    return combined
