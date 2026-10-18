"""REUSABLE DECISION PATTERN: tool selection  (#tool-selection)

Spark AI — before every user message reaches the LLM, Strands Decider 2B picks
which tool (or workflow) should handle it.  Fewer tools in the LLM's context means
fewer wrong calls, faster turns, and cheaper inference.  When the Decider is unsure
(confidence < threshold), all tools are passed to the LLM so nothing is lost.

Typed questions and options
    `tool` (choice): one option per Spark AI tool, described by its docstring, plus
    `none` ("no tool is needed; the assistant can answer directly").  Options are
    read per request from the tool registry, so adding a tool needs no retraining.

Wiring
    `SparkToolSelector` wraps `decider_kit.patterns.tool_selection.ToolSelector`.
    `SparkAgent.chat()` calls `selector.tools_for(message, history)` to get the
    narrowed list, then starts a fresh `strands.Agent` with only those tools.

How to reuse it
    Copy this file, replace `TOOLS` with your own `@tool` functions (each with a
    clear one-line docstring), and wire `SparkToolSelector` into your agent the same
    way.  The Decider question is generated automatically from the docstrings.
"""

from __future__ import annotations

from decider_kit import Decider
from decider_kit.patterns.tool_selection import ToolSelector

from .tools import TOOLS

PATTERN_TAG = "#tool-selection"

# Confidence threshold: below this the selector passes all tools to the LLM.
THRESHOLD = 0.6


class SparkToolSelector:
    """Thin wrapper that wires ToolSelector into Spark AI and exposes its log."""

    def __init__(self, decider: Decider | None = None, threshold: float = THRESHOLD):
        self.decider = decider or Decider()
        self.selector = ToolSelector(
            self.decider,
            tools=TOOLS,
            threshold=threshold,
            context="The assistant is Spark AI, a productivity assistant.",
        )

    def tools_for(self, request: str, history: str = "") -> list:
        return self.selector.tools_for(request, history)

    @property
    def log(self) -> list:
        return self.selector.log
