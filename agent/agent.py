"""Spark AI agent: Strands Agents SDK for the LLM loop, Strands Decider 2B for tool selection.

    from agent.agent import HackathonAgent
    out = HackathonAgent().chat("What is 847 * 23?")
    out["reply"], out["decisions"]

The interface (HackathonAgent.chat) is the kit contract — the demo UI, benchmark,
video, and AWS deployment all call this method unchanged.
"""

from __future__ import annotations

import time
from typing import Any

from strands import Agent

from decider_kit.llm import agent_model, default_model_id, image_blocks, strip_thinking

from .decision import SparkToolSelector
from .tools import TOOLS

NAME = "Spark AI"

SYSTEM_PROMPT = """You are Spark AI, an intelligent productivity assistant.
You help users with calculations, summarization, text rewriting, study planning, and code explanations.

Guidelines:
- For calculations, use the calculate tool and return the exact result.
- For summarization, call summarize_text and then produce the summary using the instruction field.
- For rewriting, call rewrite_text and then rewrite using the instruction field.
- For study plans, call create_study_plan and present the plan clearly.
- For code, call explain_code and explain using the instruction field.
- For general questions, answer directly without calling a tool.
- If the user's request is unclear, ask one focused clarifying question.
- Never guess at arithmetic — always use the calculator tool.
- Keep answers concise and formatted with Markdown where helpful."""


class HackathonAgent:
    """One Spark AI agent per session, with Strands Decider 2B tool selection wired in."""

    def __init__(self, model_id: str | None = None):
        self.model_id = model_id or default_model_id()
        self.selector = SparkToolSelector()
        # history per session: list of "user: ...\nassistant: ..." strings
        self._history: dict[str, list[str]] = {}
        # Strands Agent per session (preserves conversation context)
        self._agents: dict[str, Agent] = {}

    def _session_agent(self, session_id: str, narrowed_tools: list) -> Agent:
        """Return or create a Strands Agent for this session with the given tool set."""
        # Always create a fresh agent so the tool list reflects the Decider's decision.
        # The conversation history is maintained through the system prompt injection.
        return Agent(
            model=agent_model(self.model_id),
            system_prompt=SYSTEM_PROMPT,
            tools=narrowed_tools if narrowed_tools else TOOLS,
            callback_handler=None,
        )

    def _history_str(self, session_id: str) -> str:
        turns = self._history.get(session_id, [])
        return "\n".join(turns[-6:])  # last 3 exchanges

    def chat(
        self,
        message: str,
        session_id: str = "default",
        images: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Submit a message and get a reply with the Decider's tool-selection decision."""
        before = len(self.selector.log)
        t0 = time.perf_counter()

        history = self._history_str(session_id)
        narrowed_tools = self.selector.tools_for(message, history)

        spark_agent = self._session_agent(session_id, narrowed_tools)

        content = (
            [*image_blocks(images), {"text": message}]
            if images
            else message
        )
        result = spark_agent(content)
        reply = strip_thinking(str(result))

        # record history
        self._history.setdefault(session_id, [])
        self._history[session_id].append(f"user: {message}\nassistant: {reply}")

        decisions = self.selector.log[before:]
        tool_used = decisions[0]["tool"] if decisions else "none"

        return {
            "reply": reply,
            "decisions": decisions,
            "tool_used": tool_used,
            "model_id": self.model_id,
            "latency_ms": round((time.perf_counter() - t0) * 1000),
            "agent": NAME,
        }


if __name__ == "__main__":
    import json
    import sys

    a = HackathonAgent()
    prompts = sys.argv[1:] or [
        "What is 144 * 365?",
        "Summarize: The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.",
        "Explain this Python code: def add(a, b): return a + b",
    ]
    for msg in prompts:
        print(json.dumps(a.chat(msg), indent=2, default=str))
