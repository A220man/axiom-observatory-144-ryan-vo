import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BenchmarkForm } from '../components/BenchmarkForm';
import { apiClient } from '../api/client';
import type { BenchmarkResponse, BenchmarkRun, ProviderType } from '../types/api';

// Mock the API client
vi.mock('../api/client', () => ({
  apiClient: {
    benchmark: vi.fn(),
    health: vi.fn(),
  },
}));

function createMockRun(provider: ProviderType = 'simulated'): BenchmarkRun {
  return {
    id: 'abc123',
    model: 'gpt-3.5-turbo',
    provider,
    prompt: 'Test',
    max_tokens: 50,
    temperature: 0.7,
    metrics: {
      ttft_ms: 50.0,
      tpot_ms: 10.0,
      throughput_tokens_per_sec: 100.0,
      total_tokens: 100,
      prompt_tokens: 20,
      completion_tokens: 80,
    },
    created_at: new Date().toISOString(),
    status: 'completed',
  };
}

function createMockResponse(provider: ProviderType = 'simulated'): BenchmarkResponse {
  return {
    runs: [createMockRun(provider)],
    aggregate: {
      ttft_ms: 50.0,
      tpot_ms: 10.0,
      throughput_tokens_per_sec: 100.0,
      total_tokens: 100,
      prompt_tokens: 20,
      completion_tokens: 80,
    },
  };
}

describe('BenchmarkForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form with default values', () => {
    render(<BenchmarkForm />);
    expect(screen.getByLabelText('Model')).toHaveValue('gpt-3.5-turbo');
    expect(screen.getByLabelText('Provider')).toHaveValue('simulated');
    expect(screen.getByLabelText('Prompt')).toHaveValue('Explain quantum computing in simple terms.');
    // Number inputs return numeric values
    expect(screen.getByLabelText('Max Tokens')).toHaveValue(100);
    expect(screen.getByLabelText('Temperature')).toHaveValue(0.7);
    expect(screen.getByLabelText('Runs')).toHaveValue(1);
  });

  it('updates form fields on input', () => {
    render(<BenchmarkForm />);
    fireEvent.change(screen.getByLabelText('Model'), { target: { value: 'llama-3-8b' } });
    expect(screen.getByLabelText('Model')).toHaveValue('llama-3-8b');
  });

  it('calls API on submit and displays results', async () => {
    vi.mocked(apiClient.benchmark).mockResolvedValue(createMockResponse());

    render(<BenchmarkForm />);
    fireEvent.click(screen.getByText('Run Benchmark'));

    await screen.findByText('Results');
    expect(screen.getByText('Aggregate (1 run)')).toBeInTheDocument();
    // Check for throughput in the aggregate section
    const aggregateSection = screen.getByText('Aggregate (1 run)').closest('div');
    expect(aggregateSection).toHaveTextContent('100.0');
  });

  it('displays error on API failure', async () => {
    vi.mocked(apiClient.benchmark).mockRejectedValue(new Error('Network error'));

    render(<BenchmarkForm />);
    fireEvent.click(screen.getByText('Run Benchmark'));

    await screen.findByText('Network error');
  });

  it('shows loading state during request', async () => {
    let resolveFn: (value: BenchmarkResponse) => void;
    const promise = new Promise<BenchmarkResponse>((resolve) => { resolveFn = resolve; });
    vi.mocked(apiClient.benchmark).mockReturnValue(promise);

    render(<BenchmarkForm />);
    fireEvent.click(screen.getByText('Run Benchmark'));

    expect(screen.getByText('Running...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();

    resolveFn!(createMockResponse());
    await screen.findByText('Run Benchmark');
  });

  it('clears results when clear button clicked', async () => {
    vi.mocked(apiClient.benchmark).mockResolvedValue(createMockResponse());

    render(<BenchmarkForm />);
    fireEvent.click(screen.getByText('Run Benchmark'));

    await screen.findByText('Results');

    fireEvent.click(screen.getByText('Clear Results'));

    expect(screen.queryByText('Results')).not.toBeInTheDocument();
  });

  it('tests different providers', async () => {
    const providers: ProviderType[] = ['openai_compatible', 'anthropic', 'gemini', 'ollama', 'simulated'];
    
    for (const provider of providers) {
      vi.mocked(apiClient.benchmark).mockResolvedValue(createMockResponse(provider));
      
      // Unmount previous render
      const { unmount } = render(<BenchmarkForm />);
      fireEvent.change(screen.getByLabelText('Provider'), { target: { value: provider } });
      fireEvent.click(screen.getByRole('button', { name: 'Run Benchmark' }));

      await screen.findByText('Results');
      // Check provider appears in run config
      expect(screen.getByText(`Provider: ${provider}`)).toBeInTheDocument();
      
      unmount();
    }
  });
});