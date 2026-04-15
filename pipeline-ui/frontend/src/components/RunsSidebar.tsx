import { useState } from 'react';
import type { PipelineRun } from '../types';

interface Props {
  runs: PipelineRun[];
  activeRunId: string | null;
  onSelectRun: (id: string) => void;
  onCreateRun: (name: string, repo?: string) => void;
  onDeleteRun: (id: string) => void;
}

export function RunsSidebar({ runs, activeRunId, onSelectRun, onCreateRun, onDeleteRun }: Props) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [repo, setRepo] = useState('');

  const handleCreate = () => {
    if (!name.trim()) return;
    onCreateRun(name.trim(), repo.trim() || undefined);
    setName('');
    setRepo('');
    setShowForm(false);
  };

  return (
    <div className="w-56 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-3 border-b border-gray-200 flex items-center justify-between">
        <h2 className="font-semibold text-gray-700 text-sm">Pipeline Runs</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="w-6 h-6 flex items-center justify-center rounded bg-blue-500 text-white text-sm hover:bg-blue-600"
        >
          +
        </button>
      </div>

      {showForm && (
        <div className="p-3 border-b border-gray-200 space-y-2">
          <input
            type="text"
            placeholder="Run name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
          <input
            type="text"
            placeholder="owner/repo (optional)"
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
          <button
            onClick={handleCreate}
            className="w-full px-2 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Create
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {runs.map((run) => (
          <div
            key={run.id}
            onClick={() => onSelectRun(run.id)}
            className={`px-3 py-2 cursor-pointer border-b border-gray-100 group flex items-center justify-between ${
              activeRunId === run.id ? 'bg-blue-50 border-l-2 border-l-blue-500' : 'hover:bg-gray-50'
            }`}
          >
            <div className="min-w-0">
              <div className="text-sm font-medium text-gray-800 truncate">{run.name}</div>
              <div className="text-xs text-gray-400">
                {run.current_stage ? `Stage: ${run.current_stage}` : 'New'}
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeleteRun(run.id);
              }}
              className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 text-xs ml-2"
            >
              x
            </button>
          </div>
        ))}
        {runs.length === 0 && (
          <div className="p-3 text-sm text-gray-400 text-center">No runs yet</div>
        )}
      </div>
    </div>
  );
}
