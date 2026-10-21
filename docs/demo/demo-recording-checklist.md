# Demo Recording Checklist — Spark AI

Work through this list top to bottom before you hit record.

---

## 1. Environment Setup

- [ ] Close all unnecessary browser tabs and applications
- [ ] Set screen resolution to 1920×1080 (or 1280×720 minimum)
- [ ] Set browser zoom to 100%
- [ ] Hide browser bookmarks bar for a clean look
- [ ] Open VS Code with the project folder: `techspark-decider-hackathon-kit/techspark-decider-hackathon-kit/`
- [ ] Set VS Code font size to 16+ so code is readable on camera

---

## 2. API Key Verification

- [ ] Open `.env` and confirm these values are present (do NOT show this file on screen):
  - `DECIDER_MODE=ugmdu`
  - `DECIDER_URL=https://da25tnxy06gjk.cloudfront.net`
  - `DECIDER_API_KEY=dcd_live_...` (any value starting with `dcd_live_`)
  - `LLM_PROVIDER=ugmdu`
  - `LLM_MODEL_ID=qwen3.5-4b`
- [ ] Confirm the API key is NOT visible in any browser tab, terminal, or editor during recording

---

## 3. Start the Application

**Terminal 1 — Backend:**
```bash
cd techspark-decider-hackathon-kit/techspark-decider-hackathon-kit
python backend/main.py
```
Expected output: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 — Frontend:**
```bash
cd techspark-decider-hackathon-kit/techspark-decider-hackathon-kit/frontend
npm run dev
```
Expected output: `VITE v5.x  ready — Local: http://localhost:5173/`

- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 5173
- [ ] Hide both terminals before starting the recording (minimise or move off-screen)

---

## 4. Health Check

Run this in a separate terminal (not on screen):
```bash
curl http://localhost:8000/api/health
```
Expected: `{"status": "ok", "decider": "ok", ...}`

- [ ] Health endpoint returns `"status": "ok"`
- [ ] Decider field returns `"ok"` (not `"unreachable"`)

---

## 5. Pre-Demo Test (dry run — not on camera)

Test each prompt once before recording to confirm responses are working:

| Prompt | Expected tool in panel |
|--------|----------------------|
| `What is 847 * 23?` | Calculator |
| `Summarize this in bullet points: Artificial intelligence is transforming...` | Summarizer |
| `Create a study plan for Math and Physics, 5 days, 2 hours per day` | Study Planner |

- [ ] All three prompts return a response
- [ ] Activity Panel on the right shows tool name and confidence bar for each
- [ ] No error messages appear

---

## 6. Reset Before Recording

- [ ] Click the "Clear" button in the Spark AI header to clear all messages
- [ ] Confirm the empty state is showing ("What can I help you accomplish?")
- [ ] Activity Panel shows placeholder text: "Decisions appear here as Spark AI routes each request."

---

## 7. Pre-Prepare VS Code Tabs

Open these files in VS Code before recording (for the architecture scene):
- [ ] `agent/decision.py` — scroll to `THRESHOLD = 0.6` line
- [ ] `agent/agent.py` — scroll to `narrowed_tools = self.selector.tools_for(...)` line

---

## 8. Recording Settings

- [ ] Screen recorder is capturing the full screen (not a window)
- [ ] Microphone is tested — no background noise
- [ ] Notifications are disabled (Do Not Disturb mode on)
- [ ] Recording is set to export as MP4

---

## 9. During Recording — Critical Reminders

- [ ] Never show the `.env` file or any terminal that has the API key visible
- [ ] Speak clearly — pause 1 second after each narration line before moving the cursor
- [ ] Wait for the Activity Panel to fully update before moving to the next scene
- [ ] Keep cursor movements slow and deliberate

---

## 10. Post-Recording Checks

- [ ] Video is under 3 minutes (target: 2:40)
- [ ] API key is not visible in any frame
- [ ] Activity Panel is visible and readable in the architecture scene
- [ ] All three demo prompts show responses and decision data
- [ ] Audio is clear throughout

---

## Quick Prompt Reference (copy-paste during recording)

```
What is 847 * 23?
```

```
Summarize this in bullet points: Artificial intelligence is transforming industries from healthcare to finance. Machine learning models can diagnose diseases, predict markets, and automate workflows that once required teams of specialists.
```

```
Create a study plan for Math and Physics, 5 days, 2 hours per day
```
