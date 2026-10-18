"""Vercel serverless entry point for Spark AI backend.
Sits inside frontend/api/ so Vercel picks it up when Root Directory = frontend.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Project root is two levels up from frontend/api/
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from decider_kit.config import load_dotenv
load_dotenv(ROOT / ".env")

import asyncio
import re
import traceback
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Spark AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field("default", max_length=64)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()


_agents: dict[str, Any] = {}


def get_agent(session_id: str) -> Any:
    if session_id not in _agents:
        from agent.agent import HackathonAgent
        _agents[session_id] = HackathonAgent()
    return _agents[session_id]


@app.post("/api/chat")
async def chat(body: ChatRequest) -> JSONResponse:
    try:
        ag = get_agent(body.session_id)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: ag.chat(body.message, session_id=body.session_id)
        )
        decisions = result.get("decisions", [])
        confidence = decisions[0]["confidence"] if decisions else 0.0
        return JSONResponse({
            "reply": result["reply"],
            "tool_used": result.get("tool_used", "none"),
            "confidence": confidence,
            "decisions": decisions,
            "latency_ms": result.get("latency_ms", 0),
            "model_id": result.get("model_id", ""),
        })
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()
        msg = re.sub(r"dcd_[A-Za-z0-9_]+", "[key]", str(e))
        return JSONResponse({"error": msg, "code": "agent_error"}, status_code=500)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    from decider_kit import Decider
    from decider_kit.config import settings
    from decider_kit.llm import describe
    s = settings()
    decider_status = "ok"
    try:
        Decider().health()
    except Exception:  # noqa: BLE001
        decider_status = "unreachable"
    return {
        "status": "ok",
        "decider": decider_status,
        "llm_provider": os.environ.get("LLM_PROVIDER", "ugmdu"),
        "model_id": s.bedrock_model,
        "llm_description": describe(),
    }


@app.get("/api/tools")
async def tools_list() -> dict[str, Any]:
    from agent.tools import TOOLS
    result = []
    for t in TOOLS:
        spec = getattr(t, "tool_spec", None)
        if spec:
            name = spec["name"]
            desc = (spec.get("description") or name).strip().split("\n")[0]
        else:
            name = getattr(t, "__name__", str(t))
            desc = (t.__doc__ or name).strip().split("\n")[0]
        result.append({"name": name, "description": desc})
    return {"tools": result}


@app.post("/api/reset")
async def reset(body: dict = {}) -> dict[str, bool]:  # noqa: B006
    session_id = body.get("session_id", "default") if isinstance(body, dict) else "default"
    _agents.pop(session_id, None)
    return {"ok": True}
