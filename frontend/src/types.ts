export interface Decision {
  stage: string;
  tool: string;
  confidence: number;
  narrowed: boolean;
  probabilities: Record<string, number>;
  decider_ms?: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolUsed?: string;
  confidence?: number;
  decisions?: Decision[];
  latencyMs?: number;
  error?: boolean;
}

export interface ChatResponse {
  reply: string;
  tool_used: string;
  confidence: number;
  decisions: Decision[];
  latency_ms: number;
  model_id: string;
  error?: string;
}
