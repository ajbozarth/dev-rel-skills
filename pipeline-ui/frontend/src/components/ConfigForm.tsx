import { useState } from 'react';
import type { Artifact, SkillVariant } from '../types';
import { ArtifactPicker } from './ArtifactPicker';

interface Props {
  skillVariant: SkillVariant;
  inputArtifacts: Artifact[];
  onExecute: (params: Record<string, string | number | null>, inputArtifactId?: string) => void;
  isRunning: boolean;
  carryForward?: Record<string, string | number | null>;
}

export function ConfigForm({ skillVariant, inputArtifacts, onExecute, isRunning, carryForward }: Props) {
  const [values, setValues] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    for (const p of skillVariant.params) {
      const carried = carryForward?.[p.name];
      if (carried != null) {
        init[p.name] = String(carried);
      } else if (p.default != null) {
        init[p.name] = String(p.default);
      }
    }
    return init;
  });
  const [artifactId, setArtifactId] = useState<string | null>(
    inputArtifacts.length > 0 ? inputArtifacts[inputArtifacts.length - 1].id : null,
  );
  const [manualFilename, setManualFilename] = useState<string>('');
  const [useManual, setUseManual] = useState(inputArtifacts.length === 0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params: Record<string, string | number | null> = {};
    for (const p of skillVariant.params) {
      const val = values[p.name];
      if (p.type === 'artifact') {
        // If user switched to manual filename entry, pass it as the param
        if (useManual && manualFilename) {
          params[p.name] = manualFilename;
        }
        continue;
      }
      if (!val && !p.required) continue;
      if (p.type === 'integer') {
        params[p.name] = val ? parseInt(val, 10) : null;
      } else {
        params[p.name] = val || null;
      }
    }
    onExecute(params, useManual ? undefined : (artifactId ?? undefined));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {skillVariant.params.map((p) => (
        <div key={p.name}>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {p.label}
            {p.required && <span className="text-red-500 ml-1">*</span>}
          </label>
          {p.type === 'artifact' ? (
            <ArtifactPicker
              artifacts={inputArtifacts}
              selectedId={artifactId}
              onSelect={(id) => { setArtifactId(id); setUseManual(false); }}
              onManualFilename={setManualFilename}
              onManualMode={() => setUseManual(true)}
            />
          ) : (
            <input
              type={p.type === 'integer' ? 'number' : p.type === 'date' ? 'date' : 'text'}
              value={values[p.name] ?? ''}
              onChange={(e) => setValues((prev) => ({ ...prev, [p.name]: e.target.value }))}
              placeholder={p.description}
              required={p.required}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
            />
          )}
          {p.description && p.type !== 'artifact' && (
            <div className="text-xs text-gray-400 mt-0.5">{p.description}</div>
          )}
        </div>
      ))}
      <button
        type="submit"
        disabled={isRunning}
        className={`px-4 py-2 text-sm font-medium rounded ${
          isRunning
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-500 text-white hover:bg-blue-600'
        }`}
      >
        {isRunning ? 'Running...' : 'Run Stage'}
      </button>
    </form>
  );
}
