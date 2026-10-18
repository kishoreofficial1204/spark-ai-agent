import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
} from "react";
import ActivityPanel from "./components/ActivityPanel";
import Message from "./components/Message";
import SuggestionCards from "./components/SuggestionCards";
import { resetSession, sendMessage } from "./api";
import type { ChatMessage, Decision } from "./types";

const SESSION_ID = "spark-" + Math.random().toString(36).slice(2, 8);

const STATUSES = [
  "Understanding request…",
  "Selecting tool…",
  "Running tool…",
  "Preparing response…",
];

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusIdx, setStatusIdx] = useState(0);
  const [allDecisions, setAllDecisions] = useState<Decision[]>([]);
  const [lastUserMsg, setLastUserMsg] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const statusTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const startStatusCycle = () => {
    setStatusIdx(0);
    statusTimerRef.current = setInterval(() => {
      setStatusIdx((i) => (i + 1) % STATUSES.length);
    }, 1800);
  };

  const stopStatusCycle = () => {
    if (statusTimerRef.current) {
      clearInterval(statusTimerRef.current);
      statusTimerRef.current = null;
    }
  };

  const submit = useCallback(
    async (text: string) => {
      const msg = text.trim();
      if (!msg || loading) return;

      setLastUserMsg(msg);
      setInput("");
      setMessages((prev) => [
        ...prev,
        { id: Date.now().toString(), role: "user" as const, content: msg },
      ]);
      setLoading(true);
      startStatusCycle();

      try {
        const res = await sendMessage(msg, SESSION_ID);
        setAllDecisions((prev) => [...prev, ...(res.decisions ?? [])]);
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: "assistant" as const,
            content: res.reply,
            toolUsed: res.tool_used,
            confidence: res.confidence,
            decisions: res.decisions,
            latencyMs: res.latency_ms,
          },
        ]);
      } catch (e: unknown) {
        const errMsg = e instanceof Error ? e.message : "Unknown error";
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: "assistant" as const,
            content: `Sorry, something went wrong: ${errMsg}. Please try again.`,
            error: true,
          },
        ]);
      } finally {
        setLoading(false);
        stopStatusCycle();
      }
    },
    [loading]
  );

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    void submit(input);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      void submit(input);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  const handleClear = async () => {
    setMessages([]);
    setAllDecisions([]);
    setInput("");
    await resetSession(SESSION_ID);
  };

  const handleSuggestion = (prompt: string) => {
    setInput(prompt);
    textareaRef.current?.focus();
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="min-h-screen bg-page flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-surface/90 backdrop-blur border-b border-border px-6 py-3 flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          <span
            className="font-bold text-xl text-ink"
            style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            Spark AI
          </span>
        </div>
        <span className="text-xs text-muted ml-1 hidden sm:block">
          From Simple Prompts to Smart Actions
        </span>
        {!isEmpty && (
          <button
            onClick={() => void handleClear()}
            className="ml-auto text-sm text-muted hover:text-primary transition-colors"
            aria-label="Clear conversation"
          >
            Clear
          </button>
        )}
      </header>

      {/* Body */}
      <div className="flex-1 flex gap-4 px-4 sm:px-6 py-4 max-w-6xl mx-auto w-full">
        {/* Chat column */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Empty state */}
          {isEmpty && (
            <div className="flex-1 flex flex-col items-center justify-center gap-6 text-center px-4 py-12">
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-ink mb-2">
                  What can I help you accomplish?
                </h1>
                <p className="text-muted max-w-md">
                  Spark AI picks the right tool for each task — calculator,
                  summarizer, rewriter, study planner, or code explainer.
                </p>
              </div>
              <SuggestionCards onSelect={handleSuggestion} />
            </div>
          )}

          {/* Messages */}
          {!isEmpty && (
            <div className="flex-1 flex flex-col gap-3 overflow-y-auto pb-4 min-h-0">
              {messages.map((msg, i) => (
                <Message
                  key={msg.id}
                  message={msg}
                  onCopy={handleCopy}
                  onRetry={
                    msg.role === "assistant" && i === messages.length - 1
                      ? () => void submit(lastUserMsg)
                      : undefined
                  }
                />
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-surface border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                    <div className="flex items-center gap-2 text-sm text-muted">
                      <span className="flex gap-1">
                        {[0, 1, 2].map((dot) => (
                          <span
                            key={dot}
                            className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce"
                            style={{ animationDelay: `${dot * 0.15}s` }}
                          />
                        ))}
                      </span>
                      <span>{STATUSES[statusIdx]}</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}

          {/* Composer */}
          <form
            onSubmit={handleSubmit}
            className="mt-3 flex items-end gap-2 bg-surface border border-border rounded-2xl p-3 shadow-sm focus-within:border-primary transition-colors"
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything… Ctrl+Enter to send"
              rows={1}
              className="flex-1 resize-none bg-transparent text-sm text-ink placeholder-muted focus:outline-none min-h-[24px] max-h-40 leading-relaxed"
              style={{ height: "auto" }}
              onInput={(e) => {
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = `${el.scrollHeight}px`;
              }}
              disabled={loading}
              aria-label="Message input"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="shrink-0 w-9 h-9 rounded-xl bg-primary text-white flex items-center justify-center disabled:opacity-40 hover:bg-primary/90 transition-all"
              aria-label="Send message"
            >
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                <path
                  d="M22 2L11 13"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M22 2L15 22 11 13 2 9l20-7z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </form>
        </div>

        {/* Activity panel */}
        <aside className="hidden lg:flex w-72 xl:w-80 flex-col shrink-0">
          <ActivityPanel
            decisions={allDecisions}
            loading={loading}
            status={STATUSES[statusIdx]}
          />
        </aside>
      </div>
    </div>
  );
}
