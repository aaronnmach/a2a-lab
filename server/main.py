"""FastAPI entrypoint for the Echo A2A server."""

from __future__ import annotations

from typing import Any, Optional, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from .agent_card import AGENT_CARD, validate_card
    from .handlers import handle_task
except ImportError:
    from agent_card import AGENT_CARD, validate_card
    from handlers import handle_task

app = FastAPI(title="Echo A2A Agent")


class TextPart(BaseModel):
    type: str = "text"
    text: str


class FileDescriptor(BaseModel):
    url: str
    mimeType: str


class FilePart(BaseModel):
    type: str = "file"
    file: FileDescriptor


class Message(BaseModel):
    role: str
    parts: list[Union[TextPart, FilePart]] = Field(default_factory=list)


class TaskRequest(BaseModel):
    id: str
    sessionId: Optional[str] = None
    message: Message
    metadata: Optional[dict[str, Any]] = None


@app.on_event("startup")
async def validate_agent_card_on_startup() -> None:
    if not validate_card(AGENT_CARD):
        raise RuntimeError("AGENT_CARD is missing required fields.")


@app.get("/.well-known/agent.json")
async def get_agent_card() -> dict[str, Any]:
    return AGENT_CARD


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "agent": AGENT_CARD["id"]}


@app.post("/tasks/send")
async def send_task(request: TaskRequest) -> dict[str, Any]:
    if not request.message.parts:
        raise HTTPException(status_code=400, detail="message.parts must contain at least one part")

    result_text = await handle_task(request)

    return {
        "id": request.id,
        "status": {"state": "completed", "message": None},
        "artifacts": [
            {
                "index": 0,
                "name": "result",
                "parts": [{"type": "text", "text": result_text}],
            }
        ],
    }
