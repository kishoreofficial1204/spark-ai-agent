const SUGGESTIONS = [
  {
    icon: "🧮",
    label: "Solve a Calculation",
    prompt: "What is 847 * 23?",
  },
  {
    icon: "📝",
    label: "Summarize Text",
    prompt: "Summarize this in bullet points: ",
  },
  {
    icon: "✍️",
    label: "Improve Writing",
    prompt: "Rewrite this more professionally: ",
  },
  {
    icon: "📅",
    label: "Create Study Plan",
    prompt: "Create a study plan for Math and Physics, 5 days, 2 hours per day",
  },
  {
    icon: "💻",
    label: "Explain Code",
    prompt: "Explain this Python code: ",
  },
];

interface Props {
  onSelect: (prompt: string) => void;
}

export default function SuggestionCards({ onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2 justify-center">
      {SUGGESTIONS.map((s) => (
        <button
          key={s.label}
          onClick={() => onSelect(s.prompt)}
          className="flex items-center gap-2 px-4 py-2.5 bg-surface border border-border rounded-xl text-sm text-ink hover:border-primary hover:text-primary transition-all shadow-sm"
        >
          <span>{s.icon}</span>
          <span>{s.label}</span>
        </button>
      ))}
    </div>
  );
}
