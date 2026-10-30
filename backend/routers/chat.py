"""API router for the café chatbot (local LLM via Ollama)."""
from __future__ import annotations

import logging
import os
from typing import Annotated

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.data import store

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma4:cloud")

SYSTEM_PROMPT = (
    "You are the friendly assistant of Bright Bean Café. "
    "Answer ONLY using the menu data provided. "
    "Never invent items or prices. "
    "If unsure, say you don't know and suggest contacting the café. "
    "Keep answers under 3 sentences."
)


def _build_menu_context() -> str:
    """Build a compact one-line-per-item menu string from the in-memory store."""
    items = store.get_menu_items(None)
    lines = [f"{i.id}|{i.name}|{i.category}|{i.price:.2f}|{i.description}" for i in items]
    return "\n".join(lines)


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=300)


class ChatOut(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatOut)
def chat(body: ChatIn) -> ChatOut:
    """Forward a user message to Ollama with café menu context and return the reply."""
    menu_ctx = _build_menu_context()
    full_system = f"{SYSTEM_PROMPT}\n\nMenu:\n{menu_ctx}"

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": full_system},
                        {"role": "user", "content": body.message},
                    ],
                    "stream": False,
                    "options": {"num_predict": 150},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data.get("message", {}).get("content", "").strip()
            if not reply:
                reply = "I'm sorry, I couldn't generate a response."
            return ChatOut(reply=reply)

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Chat assistant is offline",
        )
    except httpx.HTTPStatusError as exc:
        logger.error("Ollama HTTP error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Chat assistant is offline",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Chat assistant timed out",
        )
