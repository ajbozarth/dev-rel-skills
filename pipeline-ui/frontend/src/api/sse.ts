import type {
  SSETextEvent,
  SSEToolUseEvent,
  SSEToolResultEvent,
  SSEThinkingEvent,
  SSECompleteEvent,
  SSEErrorEvent,
} from '../types';

export interface SSEHandler {
  onText?: (data: SSETextEvent) => void;
  onToolUse?: (data: SSEToolUseEvent) => void;
  onToolResult?: (data: SSEToolResultEvent) => void;
  onThinking?: (data: SSEThinkingEvent) => void;
  onComplete?: (data: SSECompleteEvent) => void;
  onError?: (data: SSEErrorEvent) => void;
}

export function connectSSE(executionId: string, handlers: SSEHandler): EventSource {
  const es = new EventSource(`/api/stream/${executionId}`);

  es.addEventListener('text', (e) => handlers.onText?.(JSON.parse((e as MessageEvent).data)));
  es.addEventListener('tool_use', (e) => handlers.onToolUse?.(JSON.parse((e as MessageEvent).data)));
  es.addEventListener('tool_result', (e) => handlers.onToolResult?.(JSON.parse((e as MessageEvent).data)));
  es.addEventListener('thinking', (e) => handlers.onThinking?.(JSON.parse((e as MessageEvent).data)));
  es.addEventListener('complete', (e) => {
    handlers.onComplete?.(JSON.parse((e as MessageEvent).data));
    es.close();
  });
  es.addEventListener('error', (e) => {
    const me = e as MessageEvent;
    if (me.data) {
      handlers.onError?.(JSON.parse(me.data));
    }
    es.close();
  });

  return es;
}
