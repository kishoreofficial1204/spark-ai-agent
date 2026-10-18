import type { ChatResponse } from "./types";

const BASE = "/api";

export async function sendMessage(
  message: string,
  sessionId: string
): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function resetSession(sessionId: string): Promise<void> {
  await fetch(`${BASE}/reset`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
}
