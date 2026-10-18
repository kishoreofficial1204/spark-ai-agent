# Spark AI ⚡ — From Simple Prompts to Smart Actions

An intelligent AI productivity assistant that routes every request to the right tool using **Strands Decider 2B** before the LLM sees it.

Built for the **Agent Experience Hackathon: Strands Decider** (AWS User Group Madurai, October 2026).

Built with the AWS User Group Madurai Strands Decider hackathon kit.

---

## What it does

| Request | Tool selected by Strands Decider 2B |
|---|---|
| "What is 847 * 23?" | Calculator (safe AST evaluator, never guesses) |
| "Summarize this article…" | Summarizer (short, detailed, or bullet-point) |
| "Rewrite this professionally…" | Text Rewriter |
| "Plan my study schedule for…" | Study Planner |
| "Explain this Python function…" | Code Explainer |
| "What is machine learning?" | Direct answer (no tool) |

The **decision panel** shows which tool was selected, the Decider's confidence, and the full probability breakdown for every turn.

## Agentic decision pattern

`#tool-selection` — before each user message reaches the LLM, Strands Decider 2B answers one typed `choice` question: *which tool should handle this request?* If confidence ≥ 0.6, the agent starts with only that tool. If unsure, all tools are passed to the LLM. One forward pass, calibrated confidence, no retraining needed when a tool is added.

---

## Quick start

### 1. Configure

```bash
cp .env.example .env
# edit .env: add your AWS credentials if using Bedrock
```

### 2. Backend

```bash
pip install strands-agents strands-agents-tools
pip install -r backend/requirements.txt
cd backend
python main.py
# → http://localhost:8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

Or use the kit demo UI (no React build needed):

```bash
./kit demo
# → http://localhost:8501
```

### 4. Benchmark

```bash
./kit bench --split tune   # tune threshold
./kit bench --split test   # report these numbers
```

### 5. Deploy

```bash
./kit deploy
./kit invoke "What is 144 * 365?"
```

---

## Stack

- **Agent:** Strands Agents SDK + Amazon Bedrock Nova Pro
- **Decision:** Strands Decider 2B (hosted AWS User Group Madurai API)
- **Pattern:** `#tool-selection` (`decider_kit/patterns/tool_selection.py`)
- **Backend:** Python + FastAPI
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Deployment:** Amazon Bedrock AgentCore Runtime

## Licence

Apache-2.0
