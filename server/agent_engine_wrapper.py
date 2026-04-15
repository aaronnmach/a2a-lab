import asyncio
import uuid
from types import SimpleNamespace


try:
    from .handlers import handle_task
except Exception:
    from handlers import handle_task


class EchoAgent:
    def set_up(self):
        print("EchoAgent.set_up() called")

    def query(self, *, task_id: str | None = None, message_text: str) -> dict:
        fake_request = SimpleNamespace(
            id=task_id or str(uuid.uuid4()),
            message=SimpleNamespace(
                role='user',
                parts=[SimpleNamespace(type='text', text=message_text)]
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
