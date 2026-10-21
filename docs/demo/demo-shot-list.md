# Demo Shot List — Spark AI

A concise list of every screen or recording segment needed for the video.

---

## Shot 1 — Empty State (0:00 – 0:35)
- **Type:** Screen recording
- **URL:** http://localhost:5173
- **What to show:** Full Spark AI interface — header with ⚡ logo and tagline, empty chat area, suggestion cards, Activity Panel on the right showing placeholder text
- **Duration:** ~35 seconds (covers opening + problem narration)
- **Notes:** Do not type anything yet. Slowly move cursor across the header, then to the Activity Panel.

---

## Shot 2 — Calculator Demo (0:35 – 1:00)
- **Type:** Screen recording
- **URL:** http://localhost:5173
- **What to show:**
  1. Type `What is 847 * 23?` in the message box
  2. Loading animation: "Understanding request… → Selecting tool… → Running tool…"
  3. Chat reply showing `19,481`
  4. Activity Panel updated: tool = Calculator, confidence bar filled ~85–95%, "narrowed" badge visible, probability breakdown for all tools
- **Duration:** ~25 seconds
- **Notes:** After response loads, pause 3 seconds on the Activity Panel before speaking.

---

## Shot 3 — Summarizer Demo (1:00 – 1:20)
- **Type:** Screen recording
- **URL:** http://localhost:5173
- **What to show:**
  1. Type the summarization prompt
  2. Loading animation
  3. Chat reply with bullet-point summary
  4. Activity Panel: tool = Summarizer, confidence bar, narrowed badge
- **Duration:** ~20 seconds
- **Notes:** The summary prompt is long — paste it rather than type to save time.

---

## Shot 4 — Study Planner Demo (1:20 – 1:40)
- **Type:** Screen recording
- **URL:** http://localhost:5173
- **What to show:**
  1. Type `Create a study plan for Math and Physics, 5 days, 2 hours per day`
  2. Chat reply with structured day-by-day plan
  3. Activity Panel: tool = Study Planner, confidence bar, narrowed badge
- **Duration:** ~20 seconds
- **Notes:** Scroll down slightly to show the full study plan output.

---

## Shot 5 — Code: decision.py (1:40 – 1:55)
- **Type:** Screen recording (VS Code)
- **File:** `agent/decision.py`
- **Lines to highlight:**
  - `THRESHOLD = 0.6`
  - `class SparkToolSelector:`
  - `self.selector = ToolSelector(self.decider, tools=TOOLS, threshold=threshold, ...)`
- **Duration:** ~15 seconds
- **Notes:** Use the cursor to slowly underline `THRESHOLD = 0.6`. No scrolling — keep the view steady.

---

## Shot 6 — Code: agent.py (1:55 – 2:10)
- **Type:** Screen recording (VS Code)
- **File:** `agent/agent.py`
- **Lines to highlight:**
  - `narrowed_tools = self.selector.tools_for(message, history)`
  - `spark_agent = self._session_agent(session_id, narrowed_tools)`
  - `return Agent(..., tools=narrowed_tools if narrowed_tools else TOOLS, ...)`
- **Duration:** ~15 seconds
- **Notes:** Highlight with cursor — no need to select text, just move cursor slowly past each line.

---

## Shot 7 — Kiro Steering Files (2:10 – 2:25)
- **Type:** Screen recording (VS Code)
- **What to show:** VS Code file explorer with `.kiro/steering/` folder expanded, showing steering files
- **Duration:** ~15 seconds
- **Notes:** Do not open any file that contains secrets or API keys. Only show the file tree.

---

## Shot 8 — Final State: Full Conversation (2:25 – 2:40)
- **Type:** Screen recording
- **URL:** http://localhost:5173
- **What to show:** Full chat with all three completed conversations visible. Activity Panel showing the last Decider decision. Spark AI header with the tagline "From Simple Prompts to Smart Actions" clearly visible.
- **Duration:** ~15 seconds
- **Notes:** Scroll up slowly to show all responses, then rest on the header for the final tagline.

---

## Optional Still Screenshots (for submission thumbnail or article)

| # | Description | URL / File |
|---|-------------|------------|
| A | Empty state — suggestion cards visible | http://localhost:5173 |
| B | Calculator result + Activity Panel (confidence ~90%) | http://localhost:5173 after first prompt |
| C | Study planner output (full plan visible) | http://localhost:5173 after third prompt |
| D | `decision.py` with THRESHOLD and ToolSelector highlighted | VS Code |
| E | Full conversation — all three responses | http://localhost:5173 |
