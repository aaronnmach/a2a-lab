import asyncio
import uuid
from types import SimpleNamespace

"""Combined agent and handler for deployment.

This module contains `handle_task` and `EchoAgent`. It's packaged as `agent`
so `deploy_agent_engine.py` can include `extra_packages=['./agent']` and the
remote runtime will import `agent.agent.EchoAgent` successfully.
"""


def handle_task(request) -> str:
    text_parts = [p.text for p in request.message.parts if p.type == "text"]
    combined = " ".join(text_parts).strip()

    if not combined:
        return ""

    if combined.startswith("!summarise"):
        return "This is a mock one-sentence summary of the provided text."

    return combined


class EchoAgent:
    def set_up(self):
        print("EchoAgent.set_up() called")

    def query(self, *, task_id: str | None = None, message_text: str) -> dict:
        fake_request = SimpleNamespace(
            id=task_id or str(uuid.uuid4()),
            message=SimpleNamespace(
                role="user",
                parts=[SimpleNamespace(type="text", text=message_text)],
            ),
        )

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio

                nest_asyncio.apply()
            result_text = asyncio.run(handle_task(fake_request))
        except Exception:
            result_text = asyncio.run(handle_task(fake_request))

        return {
            "id": fake_request.id,
            "status": {"state": "completed"},
            "artifacts": [{"parts": [{"type": "text", "text": result_text}]}],
        }
