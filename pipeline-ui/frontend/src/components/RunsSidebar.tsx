import { useState } from 'react';
import type { PipelineRun, PipelineType, PipelineTypeDef } from '../types';

interface Props {
  runs: PipelineRun[];
  activeRunId: string | null;
  pipelineTypes: PipelineTypeDef[];
  onSelectRun: (id: string) => void;
  onCreateRun: (name: string, repo?: string, pipelineType?: PipelineType) => void;
  onDeleteRun: (id: string) => void;
}

export function RunsSidebar({ runs, activeRunId, pipelineTypes, onSelectRun, onCreateRun, onDeleteRun }: Props) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [repo, setRepo] = useState('');
  const [pipelineType, setPipelineType] = useState<PipelineType>('feature_blog');

  const handleCreate = () => {
    if (!name.trim()) return;
    onCreateRun(name.trim(), repo.trim() || undefined, pipelineType);
    setName('');
    setRepo('');
    setPipelineType('feature_blog');
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
          <select
            value={pipelineType}
            onChange={(e) => setPipelineType(e.target.value as PipelineType)}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded bg-white"
          >
            {pipelineTypes.map((pt) => (
              <option key={pt.name} value={pt.name}>
                {pt.label}
              </option>
            ))}
          </select>
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
                <span className={`inline-block px-1 rounded text-[10px] font-medium mr-1 ${
                  run.pipeline_type === 'release_blog'
                    ? 'bg-purple-100 text-purple-600'
                    : run.pipeline_type === 'topical_blog'
                    ? 'bg-amber-100 text-amber-600'
                    : 'bg-blue-100 text-blue-600'
                }`}>
                  {pipelineTypes.find((pt) => pt.name === run.pipeline_type)?.label ?? run.pipeline_type}
                </span>
                {run.current_stage ? run.current_stage : 'New'}
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
