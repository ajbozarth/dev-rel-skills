import { useState } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { markdown } from '@codemirror/lang-markdown';
import { oneDark } from '@codemirror/theme-one-dark';

interface Props {
  content: string;
  onSave: (newContent: string) => void;
  isSaving: boolean;
}

export function MarkdownEditor({ content, onSave, isSaving }: Props) {
  const [edited, setEdited] = useState(content);
  const hasChanges = edited !== content;

  return (
    <div className="flex flex-col" style={{ maxHeight: '60vh' }}>
      <div className="flex-1 overflow-auto">
        <CodeMirror
          value={edited}
          onChange={setEdited}
          extensions={[markdown()]}
          theme={oneDark}
          height="100%"
          minHeight="300px"
        />
      </div>
      <div className="flex items-center gap-3 mt-2">
        <button
          onClick={() => onSave(edited)}
          disabled={isSaving || !hasChanges}
          className={`px-3 py-1.5 text-sm rounded ${
            isSaving || !hasChanges
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-500 text-white hover:bg-green-600'
          }`}
        >
          {isSaving ? 'Saving...' : 'Save'}
        </button>
        {hasChanges && <span className="text-sm text-yellow-600">Unsaved changes</span>}
      </div>
    </div>
  );
}
