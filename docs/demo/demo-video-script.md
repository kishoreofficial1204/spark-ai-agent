# Spark AI — Demo Video Script
**Title:** Spark AI: From Simple Prompts to Smart Actions  
**Total duration:** 2 minutes 40 seconds  
**Hackathon:** Agent Experience Hackathon — Strands Decider (AWS User Group Madurai, October 2026)

---

## Scene 1 — Opening (0:00 – 0:15) | 15 seconds

**Screen:** Browser open at http://localhost:5173 — the Spark AI chat interface (empty state).

**Narration:**
> "Meet Spark AI — an intelligent productivity assistant that knows exactly which tool to use before it even talks to the language model. From simple prompts to smart actions."

**Action:** Slowly pan the cursor across the Spark AI header and the tagline visible at the top of the page.

---

## Scene 2 — The Problem (0:15 – 0:35) | 20 seconds

**Screen:** Stay on the Spark AI UI. Point at the Activity Panel on the right side (currently empty, showing placeholder text).

**Narration:**
> "Most AI chatbots send every message straight to the language model and let it guess what to do. That means arithmetic gets approximated, specialized tasks get general answers, and there is no transparency in how the decision was made. Spark AI solves this with a dedicated decision step."

**Action:** Move cursor to highlight the Activity Panel titled "Strands Decider 2B" on the right. No typing yet.

---

## Scene 3 — Live Demo: Calculator (0:35 – 1:00) | 25 seconds

**Screen:** Chat interface. Type into the message box.

**Prompt to type:**
```
What is 847 * 23?
```

**Expected result:**
- Activity Panel shows: Tool selected = **Calculator**, confidence bar ~85–95%, narrowed = yes
- Probability breakdown lists all tools — Calculator is highest
- Chat reply: `847 × 23 = 19,481`

**Narration:**
> "I send a calculation. Watch the decision panel on the right. Strands Decider 2B fires first — it classifies this as a calculator request with high confidence and narrows the agent to only the calculator tool. The result is exact, computed by a safe AST evaluator — no guessing."

**Action:** Type the prompt, press Send, pause for the response to arrive, then point at the confidence bar and the "narrowed" badge in the panel.

---

## Scene 4 — Live Demo: Summarizer (1:00 – 1:20) | 20 seconds

**Screen:** Chat interface. Type a new message.

**Prompt to type:**
```
Summarize this in bullet points: Artificial intelligence is transforming industries from healthcare to finance. Machine learning models can diagnose diseases, predict markets, and automate workflows that once required teams of specialists.
```

**Expected result:**
- Activity Panel: Tool = **Summarizer**, confidence high, narrowed = yes
- Chat reply: A short bullet-point summary of the input text

**Narration:**
> "Now a summarization request. The Decider instantly routes it to the Summarizer tool. The agent receives focused instructions and produces a clean bullet-point summary."

**Action:** Type prompt, send, point at the updated Activity Panel showing Summarizer selected.

---

## Scene 5 — Live Demo: Study Planner (1:20 – 1:40) | 20 seconds

**Screen:** Chat interface.

**Prompt to type:**
```
Create a study plan for Math and Physics, 5 days, 2 hours per day
```

**Expected result:**
- Activity Panel: Tool = **Study Planner**, confidence high, narrowed = yes
- Chat reply: A structured day-by-day schedule (Day 1: Math, Day 2: Math, Day 3: Physics, etc.)

**Narration:**
> "A study planning request. The Decider picks the Study Planner tool. The agent builds a structured day-by-day schedule — no guesswork, the right tool every time."

**Action:** Type prompt, send, scroll through the study plan response.

---

## Scene 6 — Architecture Explanation (1:40 – 2:10) | 30 seconds

**Screen:** Switch to VS Code showing `agent/decision.py` — specifically the `SparkToolSelector` class and the `THRESHOLD = 0.6` line. Then briefly show `agent/agent.py` — the `chat()` method where `selector.tools_for()` is called.

**Narration:**
> "Here is how it works under the hood. Before every user message reaches the LLM, `SparkToolSelector` calls Strands Decider 2B with a typed choice question: which of these five tools should handle this request?  
> The Decider returns a label — calculator, summarizer, rewriter, study planner, code explainer, or none — along with a confidence score.  
> If confidence is above 0.6, the Strands Agent is started with only that one tool. If the Decider is unsure, all tools are passed to the LLM so nothing is lost.  
> The LLM provider in this demo is the AWS User Group Madurai cloud running Qwen3.5-4B. Switching to Amazon Bedrock Nova Pro requires only one line in the `.env` file."

**Action:**
1. Show `decision.py` — highlight `THRESHOLD = 0.6` and `ToolSelector` import
2. Show `agent.py` — highlight `narrowed_tools = self.selector.tools_for(message, history)` and `Agent(..., tools=narrowed_tools)`
3. Return to browser

---

## Scene 7 — Development with Kiro (2:10 – 2:25) | 15 seconds

**Screen:** VS Code showing the `.kiro/` folder structure briefly, or show the open editor tabs.

**Narration:**
> "I built Spark AI using Kiro, AWS's AI-powered IDE. Kiro helped me understand the hackathon kit's architecture, navigate across files, and implement the tool selection pattern correctly. The steering files in `.kiro/steering/` guided every step — from agent design to the decision threshold."

**Action:** Show the `.kiro/steering/` folder open in the file explorer, then close it.

---

## Scene 8 — Conclusion (2:25 – 2:40) | 15 seconds

**Screen:** Return to browser — show the chat with all three completed responses and the Activity Panel showing the last decision.

**Narration:**
> "Spark AI shows how a small, specialized model — Strands Decider 2B — makes an LLM agent faster, more accurate, and completely transparent. Every decision is visible. Every tool is picked for a reason.  
> From simple prompts to smart actions."

**Action:** Slowly scroll up to show all three conversations. End on the Spark AI header with the tagline visible.

---

*End of script. Total: ~2 minutes 40 seconds.*
