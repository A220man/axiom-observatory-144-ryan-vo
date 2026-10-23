export type ProviderType =
  | 'openai_compatible'
  | 'anthropic'
  | 'gemini'
  | 'ollama'
  | 'simulated';

export interface BenchmarkRequest {
  model: string;
  provider: ProviderType;
  prompt: string;
  max_tokens: number;
  temperature: number;
  num_runs: number;
}

export interface TokenMetrics {
  ttft_ms: number;
  tpot_ms: number;
  throughput_tokens_per_sec: number;
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
}

export interface BenchmarkRun {
  id: string;
  model: string;
  provider: ProviderType;
  prompt: string;
  max_tokens: number;
  temperature: number;
  metrics: TokenMetrics;
  created_at: string;
  status: 'completed' | 'failed';
  error?: string;
}

export interface BenchmarkResponse {
  runs: BenchmarkRun[];
  aggregate?: TokenMetrics;
}

export interface HealthResponse {
  status: string;
  version: string;
  service: string;
}