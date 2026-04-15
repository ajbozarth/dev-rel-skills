import { useState } from 'react';
import type { Artifact } from '../types';

interface Props {
  artifacts: Artifact[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  /** Called when user types a filename manually (no artifact selected) */
  onManualFilename?: (filename: string) => void;
  /** Called when user switches to manual filename entry */
  onManualMode?: () => void;
}

export function ArtifactPicker({ artifacts, selectedId, onSelect, onManualFilename, onManualMode }: Props) {
  const [manualMode, setManualMode] = useState(artifacts.length === 0);
  const [filename, setFilename] = useState('');

  if (manualMode) {
    return (
      <div className="space-y-1">
        <input
          type="text"
          value={filename}
          onChange={(e) => {
            setFilename(e.target.value);
            onManualFilename?.(e.target.value);
          }}
          placeholder="Enter filename (e.g. blog-release-v1.0.md)"
          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
        />
        {artifacts.length > 0 && (
          <button
            type="button"
            onClick={() => setManualMode(false)}
            className="text-xs text-blue-500 hover:underline"
          >
            Pick from artifacts instead
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <select
        value={selectedId ?? ''}
        onChange={(e) => onSelect(e.target.value)}
        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded bg-white"
      >
        <option value="">Select an artifact...</option>
        {artifacts.map((a) => (
          <option key={a.id} value={a.id}>
            {a.filename} ({a.stage})
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={() => { setManualMode(true); onManualMode?.(); }}
        className="text-xs text-blue-500 hover:underline"
      >
        Enter filename manually instead
      </button>
    </div>
  );
}
