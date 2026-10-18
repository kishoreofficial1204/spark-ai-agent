# Spark AI

- **Pitch:** an AI productivity assistant that routes every request to the right tool using Strands Decider 2B before the LLM sees it — so arithmetic is always exact, summaries are always focused, and every action is transparent.
- **Who it is for:** students who need help learning and coding, developers who want quick code explanations, professionals who need to summarize or rewrite content, and general users who want to get things done in plain language.
- **Features:**
  - calculator (safe AST evaluator — never guesses arithmetic);
  - smart summarizer (short, detailed, or bullet-point);
  - text rewriter (professional, simple, concise, formal);
  - study planner (day-by-day schedule from subjects + deadline);
  - code explainer (language auto-detected, error diagnosis included);
  - general AI assistant for everything else.
- **The decision handed to Strands Decider 2B:** before each user message reaches the LLM, which tool should handle this request? (`#tool-selection`)
- **Why a decision model:** narrowing the agent's tool context before the LLM runs reduces wrong tool calls, lowers token usage, and makes the routing transparent and benchmarkable.
- **Amazon Bedrock:** the conversation and tool use (Amazon Nova Pro by default).
