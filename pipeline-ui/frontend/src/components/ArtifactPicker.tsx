import type { Artifact } from '../types';

interface Props {
  artifacts: Artifact[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function ArtifactPicker({ artifacts, selectedId, onSelect }: Props) {
  if (artifacts.length === 0) {
    return <div className="text-sm text-gray-400 italic">No artifacts available from previous stages</div>;
  }

  return (
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
  );
}
