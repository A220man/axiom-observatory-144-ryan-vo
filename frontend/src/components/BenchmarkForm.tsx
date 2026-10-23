import { useState } from 'react';
import type { BenchmarkRequest, ProviderType, TokenMetrics } from '../types/api';
import { useBenchmark } from '../hooks/useBenchmark';

const PROVIDERS: { value: ProviderType; label: string }[] = [
  { value: 'simulated', label: 'Simulated (Local)' },
  { value: 'openai_compatible', label: 'OpenAI Compatible' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'gemini', label: 'Gemini' },
  { value: 'ollama', label: 'Ollama' },
];

export function BenchmarkForm() {
  const [formData, setFormData] = useState<BenchmarkRequest>({
    model: 'gpt-3.5-turbo',
    provider: 'simulated',
    prompt: 'Explain quantum computing in simple terms.',
    max_tokens: 100,
    temperature: 0.7,
    num_runs: 1,
  });
  const { loading, result, error, runBenchmark, clear } = useBenchmark();

  const handleChange = (field: keyof BenchmarkRequest, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runBenchmark(formData);
  };

  const formatMetrics = (metrics: TokenMetrics | undefined) => {
    if (!metrics) return null;
    return (
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-value">{metrics.ttft_ms.toFixed(1)}</span>
          <span className="metric-label">TTFT (ms)</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics.tpot_ms.toFixed(1)}</span>
          <span className="metric-label">TPOT (ms)</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics.throughput_tokens_per_sec.toFixed(1)}</span>
          <span className="metric-label">Tokens/sec</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics.completion_tokens}</span>
          <span className="metric-label">Output Tokens</span>
        </div>
      </div>
    );
  };

  return (
    <div className="benchmark-container">
      <form onSubmit={handleSubmit} className="benchmark-form">
        <h2>Inference Benchmark</h2>

        <div className="form-group">
          <label htmlFor="model">Model</label>
          <input
            id="model"
            type="text"
            value={formData.model}
            onChange={e => handleChange('model', e.target.value)}
            placeholder="e.g., gpt-3.5-turbo, llama-3-8b"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="provider">Provider</label>
          <select
            id="provider"
            value={formData.provider}
            onChange={e => handleChange('provider', e.target.value as ProviderType)}
          >
            {PROVIDERS.map(p => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="prompt">Prompt</label>
          <textarea
            id="prompt"
            value={formData.prompt}
            onChange={e => handleChange('prompt', e.target.value)}
            rows={4}
            placeholder="Enter your prompt here..."
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="max_tokens">Max Tokens</label>
            <input
              id="max_tokens"
              type="number"
              value={formData.max_tokens}
              onChange={e => handleChange('max_tokens', parseInt(e.target.value, 10))}
              min={1}
              max={4096}
            />
          </div>

          <div className="form-group">
            <label htmlFor="temperature">Temperature</label>
            <input
              id="temperature"
              type="number"
              value={formData.temperature}
              onChange={e => handleChange('temperature', parseFloat(e.target.value))}
              min={0}
              max={2}
              step={0.1}
            />
          </div>

          <div className="form-group">
            <label htmlFor="num_runs">Runs</label>
            <input
              id="num_runs"
              type="number"
              value={formData.num_runs}
              onChange={e => handleChange('num_runs', parseInt(e.target.value, 10))}
              min={1}
              max={10}
            />
          </div>
        </div>

        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Running...' : 'Run Benchmark'}
        </button>

        {error && <div className="error-message">{error}</div>}
      </form>

      {result && (
        <div className="results-section">
          <h3>Results</h3>
          {result.aggregate && (
            <div className="aggregate-results">
              <h4>Aggregate ({result.runs.length} run{result.runs.length > 1 ? 's' : ''})</h4>
              {formatMetrics(result.aggregate)}
            </div>
          )}

          <div className="runs-list">
            {result.runs.map((run, idx) => (
              <div key={run.id} className="run-card">
                <div className="run-header">
                  <span className="run-id">Run {idx + 1} ({run.id})</span>
                  <span className="run-status">{run.status}</span>
                </div>
                <div className="run-config">
                  <span>Model: {run.model}</span>
                  <span>Provider: {run.provider}</span>
                  <span>Temp: {run.temperature}</span>
                </div>
                {formatMetrics(run.metrics)}
              </div>
            ))}
          </div>

          <button onClick={clear} className="btn-secondary">
            Clear Results
          </button>
        </div>
      )}
    </div>
  );
}