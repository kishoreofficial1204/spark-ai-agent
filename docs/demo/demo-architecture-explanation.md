# Spark AI — Architecture Explanation
**Audience:** Hackathon judges and college students  
**Level:** Beginner-friendly, technically accurate

---

## The Big Picture

Spark AI is a productivity assistant that can do five things: calculate, summarize, rewrite, plan a study schedule, and explain code. The key difference from a normal chatbot is **how it decides which of these to do**.

Most chatbots send every message directly to the language model and let it figure out what to do. Spark AI adds a dedicated decision step before the language model ever sees the message.

```
User message
     │
     ▼
┌──────────────────────────┐
│   Strands Decider 2B     │  ← small, fast classification model
│   "Which tool?"          │    hosted at AWS User Group Madurai API
└──────────────────────────┘
     │
     │  returns: tool name + confidence score (0 to 1)
     ▼
┌──────────────────────────┐
│   Strands Agent (LLM)    │  ← language model (Qwen3.5-4B via UG Madurai cloud,
│   runs with 1 tool only  │    or Amazon Bedrock Nova Pro)
│   (if confidence ≥ 0.6)  │
└──────────────────────────┘
     │
     ▼
  Reply to user
```

---

## Step-by-Step: What Happens on Every Message

### Step 1 — User sends a message
The message goes to the FastAPI backend (`backend/main.py`) via `POST /api/chat`.

### Step 2 — Strands Decider 2B classifies the request
The backend calls `SparkToolSelector.tools_for(message)` (in `agent/decision.py`).

Inside that function, a `Decider` client sends the message to the Strands Decider 2B API with a typed **choice question**:

```
"Which tool should handle this request?"
Options:
  calculate      — "Evaluate a mathematical expression and return the exact numeric result."
  summarize_text — "Summarize provided text in short, detailed, or bullet-point style."
  rewrite_text   — "Rewrite provided text in a chosen style: professional, simple, concise, or formal."
  create_study_plan — "Generate a structured day-by-day study plan..."
  explain_code   — "Explain what a code snippet does; optionally diagnose an error message."
  none           — "No tool is needed; the assistant can answer directly."
```

The option descriptions come directly from the one-line docstrings on each `@tool` function in `agent/tools.py`. Adding a new tool requires no retraining — the Decider reads the description at runtime.

### Step 3 — Confidence check
The Decider returns the selected tool name and a confidence score between 0 and 1.

- If confidence **≥ 0.6** → the agent is started with **only that one tool** (narrowed)
- If confidence **< 0.6** → all five tools are passed to the LLM and it decides (nothing lost)

This threshold is set in `agent/decision.py`:
```python
THRESHOLD = 0.6
```

### Step 4 — Strands Agent runs with the selected tool
A `strands.Agent` is created with the narrowed tool list. The Strands Agents SDK handles the full LLM loop: the model receives the message, calls the tool if needed, gets the result, and writes a reply.

For example, if the Decider selected `calculate`:
- The agent calls `calculate("847 * 23")`
- The tool uses a safe Python AST evaluator (no `eval()`) and returns `{"result": 19481}`
- The LLM formats that result into a clear reply

### Step 5 — Decision data is returned to the frontend
The backend response includes `tool_used`, `confidence`, and the full `decisions` array with all probabilities. The React frontend displays this in the Activity Panel on the right side of the screen.

---

## Why This Architecture Matters

| Without Decider | With Decider (Spark AI) |
|----------------|------------------------|
| LLM sees all tools every time | LLM sees only 1 relevant tool |
| May call the wrong tool | Tool is pre-selected before LLM call |
| Arithmetic can be approximated | Calculator is always used for math |
| No visibility into tool selection | Every decision is shown in the panel |
| Adding a tool requires prompt tuning | Adding a tool just needs a docstring |

---

## Key Files

| File | What it does |
|------|-------------|
| `agent/decision.py` | Wires Strands Decider 2B into Spark AI. Defines `SparkToolSelector`. |
| `agent/agent.py` | The main `HackathonAgent` class. Calls `selector.tools_for()` then runs `strands.Agent`. |
| `agent/tools.py` | The five `@tool` functions. Their docstrings are the Decider's option descriptions. |
| `decider_kit/patterns/tool_selection.py` | Reusable `ToolSelector` pattern from the hackathon kit. |
| `decider_kit/client.py` | HTTP client that calls the Strands Decider 2B API. |
| `backend/main.py` | FastAPI server. Exposes `/api/chat`, `/api/health`, `/api/tools`. |
| `frontend/src/components/ActivityPanel.tsx` | React component that displays the Decider's decision in real time. |

---

## LLM Provider Configuration

The LLM provider is set in `.env`:

```
LLM_PROVIDER=ugmdu          # AWS User Group Madurai cloud (used in this demo)
LLM_MODEL_ID=qwen3.5-4b

# Switch to Bedrock with one line:
# LLM_PROVIDER=bedrock
# BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
```

The `decider_kit/llm.py` module reads this and returns the correct Strands model object (`BedrockModel`, `OllamaModel`, or `OpenAIModel`). The agent code never changes — only the config.

---

## Pattern Tag

This project implements the **`#tool-selection`** agentic pattern from the hackathon kit:  
`decider_kit/patterns/tool_selection.py`

The pattern is reusable: copy `agent/decision.py`, replace `TOOLS` with your own `@tool` functions (each with a clear one-line docstring), and wire `SparkToolSelector` into your agent the same way. No retraining needed when a tool is added.
