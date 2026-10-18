import type { Decision } from "../types";

interface Props {
  decisions: Decision[];
  loading: boolean;
  status: string;
}

const TOOL_LABELS: Record<string, string> = {
  calculate: "Calculator",
  summarize_text: "Summarizer",
  rewrite_text: "Rewriter",
  create_study_plan: "Study Planner",
  explain_code: "Code Explainer",
  none: "Direct Answer",
};

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = value >= 0.7 ? "#356DF3" : value >= 0.5 ? "#8057E8" : "#94A3B8";
  return (
    <div className="flex items-center gap-2 text-xs font-mono">
      <div className="flex-1 h-1.5 bg-[#E4EAF3] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="text-muted w-8 text-right">{pct}%</span>
    </div>
  );
}

export default function ActivityPanel({ decisions, loading, status }: Props) {
  const latest = decisions[decisions.length - 1];

  return (
    <div className="bg-surface border border-border rounded-xl p-4 flex flex-col gap-3 min-w-0">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold text-muted uppercase tracking-wider">
          Strands Decider 2B
        </span>
        {loading && (
          <span className="ml-auto inline-flex items-center gap-1 text-xs text-primary">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            {status}
          </span>
        )}
      </div>

      {!latest && !loading && (
        <p className="text-sm text-muted italic">
          Decisions appear here as Spark AI routes each request.
        </p>
      )}

      {latest && (
        <div className="flex flex-col gap-2">
          {/* tool selected */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-ink">
              {TOOL_LABELS[latest.tool] ?? latest.tool}
            </span>
            <span
              className={`text-xs font-mono px-2 py-0.5 rounded-full border ${
                latest.narrowed
                  ? "border-primary text-primary bg-primary/5"
                  : "border-muted text-muted"
              }`}
            >
              {latest.narrowed ? "narrowed" : "all tools"}
            </span>
          </div>

          {/* confidence bar */}
          <ConfidenceBar value={latest.confidence} />

          {/* probability breakdown */}
          <div className="flex flex-col gap-1 mt-1">
            {Object.entries(latest.probabilities)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 5)
              .map(([tool, prob]) => (
                <div key={tool} className="flex items-center gap-2 text-xs">
                  <span className="w-28 truncate text-muted font-mono">
                    {TOOL_LABELS[tool] ?? tool}
                  </span>
                  <div className="flex-1 h-1 bg-[#E4EAF3] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full bg-violet/60"
                      style={{ width: `${Math.round(prob * 100)}%` }}
                    />
                  </div>
                  <span className="w-8 text-right text-muted font-mono">
                    {Math.round(prob * 100)}%
                  </span>
                </div>
              ))}
          </div>

          {latest.decider_ms !== undefined && (
            <p className="text-xs text-muted font-mono mt-1">
              Decider latency: {Math.round(latest.decider_ms)} ms
            </p>
          )}
        </div>
      )}

      <p className="text-xs text-muted/60 mt-auto pt-2 border-t border-border">
        Built with the AWS User Group Madurai Strands Decider hackathon kit
      </p>
    </div>
  );
}
