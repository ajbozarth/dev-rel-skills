import { useCallback, useEffect, useRef, useState } from 'react';
import { connectSSE } from '../api/sse';

export interface LogEntry {
  type: 'text' | 'tool_use' | 'tool_result' | 'thinking';
  content: string;
  detail?: string;
  timestamp: number;
}

export interface StreamState {
  log: LogEntry[];
  status: 'idle' | 'streaming' | 'complete' | 'error';
  errorMessage: string | null;
  artifactIds: string[];
  costUsd: number | null;
}

export function useSSE() {
  const [stream, setStream] = useState<StreamState>({
    log: [],
    status: 'idle',
    errorMessage: null,
    artifactIds: [],
    costUsd: null,
  });
  const esRef = useRef<EventSource | null>(null);

  const startStreaming = useCallback((executionId: string) => {
    setStream({ log: [], status: 'streaming', errorMessage: null, artifactIds: [], costUsd: null });

    esRef.current = connectSSE(executionId, {
      onText: (data) => {
        setStream((prev) => ({
          ...prev,
          log: [...prev.log, { type: 'text', content: data.text, timestamp: Date.now() }],
        }));
      },
      onToolUse: (data) => {
        setStream((prev) => ({
          ...prev,
          log: [
            ...prev.log,
            { type: 'tool_use', content: data.input_summary, detail: data.tool, timestamp: Date.now() },
          ],
        }));
      },
      onToolResult: (data) => {
        setStream((prev) => ({
          ...prev,
          log: [
            ...prev.log,
            { type: 'tool_result', content: data.truncated_output, detail: data.tool_use_id, timestamp: Date.now() },
          ],
        }));
      },
      onThinking: (data) => {
        setStream((prev) => ({
          ...prev,
          log: [...prev.log, { type: 'thinking', content: data.text, timestamp: Date.now() }],
        }));
      },
      onComplete: (data) => {
        setStream((prev) => ({
          ...prev,
          status: 'complete',
          artifactIds: data.artifact_ids,
          costUsd: data.cost_usd,
        }));
      },
      onError: (data) => {
        setStream((prev) => ({
          ...prev,
          status: 'error',
          errorMessage: data.message,
        }));
      },
    });
  }, []);

  const stopStreaming = useCallback(() => {
    esRef.current?.close();
    esRef.current = null;
  }, []);

  useEffect(() => () => { esRef.current?.close(); }, []);

  return { stream, startStreaming, stopStreaming };
}
