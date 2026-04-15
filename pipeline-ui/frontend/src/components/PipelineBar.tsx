import type { Stage, StageDefinition, StageExecution } from '../types';

interface Props {
  registry: StageDefinition[];
  stageOrder: Stage[];
  selectedStage: Stage;
  onSelectStage: (stage: Stage) => void;
  executions: StageExecution[];
  researchStatus?: string | null;
}

function getStageStatus(stage: Stage, executions: StageExecution[]): 'pending' | 'running' | 'completed' | 'failed' {
  const stageExecs = executions.filter((e) => e.stage === stage);
  if (stageExecs.some((e) => e.status === 'completed')) return 'completed';
  if (stageExecs.some((e) => e.status === 'running')) return 'running';
  if (stageExecs.some((e) => e.status === 'failed')) return 'failed';
  return 'pending';
}

const statusIcon: Record<string, string> = {
  pending: '\u25CB',     // empty circle
  running: '\u25CF',     // filled circle (animated via CSS)
  completed: '\u2713',   // checkmark
  failed: '\u2717',      // X
};

const statusColor: Record<string, string> = {
  pending: 'text-gray-400 border-gray-300',
  running: 'text-blue-500 border-blue-500 animate-pulse',
  completed: 'text-green-600 border-green-500',
  failed: 'text-red-500 border-red-500',
};

export function PipelineBar({ registry, stageOrder, selectedStage, onSelectStage, executions, researchStatus }: Props) {
  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3">
      {researchStatus && (
        <div className={`text-xs mb-2 flex items-center gap-1.5 ${
          researchStatus === 'completed' ? 'text-green-600' :
          researchStatus === 'running' ? 'text-blue-500' :
          researchStatus === 'failed' ? 'text-red-500' : 'text-gray-400'
        }`}>
          {researchStatus === 'running' && <span className="animate-pulse">&#9679;</span>}
          {researchStatus === 'completed' && <span>&#10003;</span>}
          {researchStatus === 'failed' && <span>&#10007;</span>}
          {researchStatus === 'running' ? 'Researching project...' :
           researchStatus === 'completed' ? 'Project context ready' :
           researchStatus === 'failed' ? 'Research failed' : ''}
        </div>
      )}
      <div className="flex items-center gap-1">
        {stageOrder.map((stage, i) => {
          const def = registry.find((s) => s.stage === stage);
          const status = getStageStatus(stage, executions);
          const isSelected = stage === selectedStage;

          return (
            <div key={stage} className="flex items-center">
              {i > 0 && <span className="text-gray-300 mx-1">&rarr;</span>}
              <button
                onClick={() => onSelectStage(stage)}
                className={`px-3 py-1.5 rounded-full text-sm border transition-all ${statusColor[status]} ${
                  isSelected
                    ? 'ring-2 ring-blue-400 ring-offset-1 bg-blue-50 font-semibold'
                    : 'bg-white hover:bg-gray-50'
                }`}
              >
                <span className="mr-1">{statusIcon[status]}</span>
                {def?.label ?? stage}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
