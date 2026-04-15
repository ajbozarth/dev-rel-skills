import { PipelineBar } from './components/PipelineBar';
import { RunsSidebar } from './components/RunsSidebar';
import { StagePanel } from './components/StagePanel';
import { usePipeline } from './hooks/usePipeline';

export default function App() {
  const pipeline = usePipeline();

  return (
    <div className="flex h-screen bg-gray-50">
      <RunsSidebar
        runs={pipeline.runs}
        activeRunId={pipeline.activeRunId}
        onSelectRun={pipeline.setActiveRunId}
        onCreateRun={pipeline.createRun}
        onDeleteRun={pipeline.deleteRun}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        {pipeline.activeRun ? (
          <>
            <PipelineBar
              registry={pipeline.registry}
              selectedStage={pipeline.selectedStage}
              onSelectStage={pipeline.selectStage}
              executions={pipeline.activeRun.executions}
            />
            <StagePanel
              run={pipeline.activeRun}
              stage={pipeline.selectedStage}
              registry={pipeline.registry}
              onRefresh={pipeline.refreshRun}
              onSelectStage={pipeline.selectStage}
              getInputArtifacts={pipeline.getInputArtifacts}
              getStageExecutions={pipeline.getStageExecutions}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400 text-lg">
            Select or create a pipeline run to get started
          </div>
        )}
      </div>
    </div>
  );
}
