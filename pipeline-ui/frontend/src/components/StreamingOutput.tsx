import { useEffect, useRef, useState } from 'react';
import type { LogEntry } from '../hooks/useSSE';

interface Props {
  log: LogEntry[];
  status: 'idle' | 'streaming' | 'complete' | 'error';
  errorMessage: string | null;
}

export function StreamingOutput({ log, status, errorMessage }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [collapsedThinking, setCollapsedThinking] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [log]);

  const toggleThinking = (idx: number) => {
    setCollapsedThinking((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  if (log.length === 0 && status === 'idle') {
    return <div className="text-sm text-gray-400 italic p-4">Run a stage to see output here.</div>;
  }

  return (
    <div>
      <div ref={containerRef} className="terminal-output">
        {log.map((entry, i) => {
          if (entry.type === 'text') {
            return (
              <div key={i} className="whitespace-pre-wrap mb-1">
                {entry.content}
              </div>
            );
          }
          if (entry.type === 'tool_use') {
            return (
              <div key={i} className="tool-use-entry mb-1">
                <span className="text-gray-500 mr-1">&gt;</span>
                <span className="font-semibold">{entry.detail}</span>
                <span className="text-gray-400 ml-2">{entry.content}</span>
              </div>
            );
          }
          if (entry.type === 'tool_result') {
            return (
              <div key={i} className="text-gray-500 text-xs pl-4 mb-1 max-h-20 overflow-hidden">
                {entry.content}
              </div>
            );
          }
          if (entry.type === 'thinking') {
            const collapsed = !collapsedThinking.has(i);
            return (
              <div key={i} className="thinking-block mb-1">
                <span
                  onClick={() => toggleThinking(i)}
                  className="cursor-pointer select-none"
                >
                  {collapsed ? '\u25B8' : '\u25BE'} Thinking...
                </span>
                {!collapsed && (
                  <div className="pl-4 text-xs whitespace-pre-wrap mt-1">{entry.content}</div>
                )}
              </div>
            );
          }
          return null;
        })}
      </div>
      <div className="mt-2 text-sm flex items-center gap-2">
        {status === 'streaming' && (
          <>
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span className="text-blue-600">Running...</span>
          </>
        )}
        {status === 'complete' && (
          <span className="text-green-600 font-medium">Complete</span>
        )}
        {status === 'error' && (
          <span className="text-red-600">Error: {errorMessage}</span>
        )}
      </div>
    </div>
  );
}
