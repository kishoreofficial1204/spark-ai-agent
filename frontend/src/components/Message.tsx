import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../types";

const TOOL_LABELS: Record<string, string> = {
  calculate: "Calculator",
  summarize_text: "Summarizer",
  rewrite_text: "Rewriter",
  create_study_plan: "Study Planner",
  explain_code: "Code Explainer",
  none: "Direct answer",
};

interface Props {
  message: ChatMessage;
  onCopy: (text: string) => void;
  onRetry?: () => void;
}

export default function Message({ message, onCopy, onRetry }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} group`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-primary text-white rounded-tr-sm"
            : message.error
            ? "bg-red-50 border border-red-200 rounded-tl-sm"
            : "bg-surface border border-border rounded-tl-sm"
        }`}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        ) : (
          <>
            <div className="prose text-sm text-ink max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>

            {/* meta row */}
            {!message.error && (
              <div className="flex items-center gap-3 mt-2 pt-2 border-t border-border/50">
                {message.toolUsed && (
                  <span className="text-xs text-muted font-mono">
                    {TOOL_LABELS[message.toolUsed] ?? message.toolUsed}
                    {message.confidence !== undefined &&
                      ` · ${Math.round(message.confidence * 100)}%`}
                  </span>
                )}
                {message.latencyMs && (
                  <span className="text-xs text-muted/60 font-mono ml-auto">
                    {message.latencyMs} ms
                  </span>
                )}
                {/* copy button */}
                <button
                  onClick={() => onCopy(message.content)}
                  className="text-xs text-muted hover:text-primary transition-colors ml-1"
                  title="Copy"
                  aria-label="Copy response"
                >
                  Copy
                </button>
                {onRetry && (
                  <button
                    onClick={onRetry}
                    className="text-xs text-muted hover:text-primary transition-colors"
                    title="Retry"
                    aria-label="Retry"
                  >
                    Retry
                  </button>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
