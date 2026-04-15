"""Optional bonus ReverseAgent FastAPI server."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from reverse_agent_card import REVERSE_AGENT_CARD

app = FastAPI(title="Reverse A2A Agent")


class TextPart(BaseModel):
    type: str = "text"
    text: str


class Message(BaseModel):
    role: str
    parts: list[TextPart]


class TaskRequest(BaseModel):
    id: str
    sessionId: Optional[str] = None
    message: Message
    metadata: Optional[dict[str, Any]] = None


@app.get('/.well-known/agent.json')
async def get_agent_card() -> dict[str, Any]:
    return REVERSE_AGENT_CARD


@app.get('/health')
async def health() -> dict[str, str]:
    return {"status": "ok", "agent": REVERSE_AGENT_CARD["id"]}


@app.post('/tasks/send')
async def send_task(request: TaskRequest) -> dict[str, Any]:
    if not request.message.parts:
        raise HTTPException(status_code=400, detail='message.parts must contain at least one part')

    text = ' '.join(part.text for part in request.message.parts if part.type == 'text')
    reversed_text = ' '.join(reversed(text.split()))
    return {
        "id": request.id,
        "status": {"state": "completed", "message": None},
        "artifacts": [{"index": 0, "name": "result", "parts": [{"type": "text", "text": reversed_text}]}],
    }
