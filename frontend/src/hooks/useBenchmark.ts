import { useState, useCallback } from 'react';
import type { BenchmarkRequest, BenchmarkResponse } from '../types/api';
import { apiClient } from '../api/client';

export function useBenchmark() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BenchmarkResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runBenchmark = useCallback(async (request: BenchmarkRequest) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.benchmark(request);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Benchmark failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { loading, result, error, runBenchmark, clear };
}