"""Spark AI — FastAPI backend.

Endpoints:
  POST /api/chat    submit a message, get an agent reply
  GET  /api/health  decider + LLM status
  GET  /api/tools   list available tools
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# make the kit root importable when running `python backend/main.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from decider_kit.config import load_dotenv

load_dotenv()

app = FastAPI(title="Spark AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:8501",   # kit demo
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8501",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field("default", max_length=64)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()


class ChatResponse(BaseModel):
    reply: str
    tool_used: str
    confidence: float
    decisions: list[dict[str, Any]]
    latency_ms: int
    model_id: str


# ---------------------------------------------------------------------------
# Lazy agent singleton per session
# ---------------------------------------------------------------------------

_agents: dict[str, Any] = {}


def get_agent(session_id: str) -> Any:
    if session_id not in _agents:
        from agent.agent import HackathonAgent
        _agents[session_id] = HackathonAgent()
    return _agents[session_id]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> JSONResponse:
    import asyncio, re, traceback
    try:
        ag = get_agent(body.session_id)
        # Run the blocking Strands agent in a thread so the async loop isn't blocked
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
        "llm_provider": os.environ.get("LLM_PROVIDER", "bedrock"),
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
async def reset(body: dict[str, str] = {}) -> dict[str, bool]:  # noqa: B006
    session_id = body.get("session_id", "default")
    _agents.pop(session_id, None)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, timeout_keep_alive=120)
