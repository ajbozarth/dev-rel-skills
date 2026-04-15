import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import type { Artifact, PipelineRunDetail, Stage, StageDefinition, StageExecution } from '../types';
import { useSSE } from '../hooks/useSSE';
import { ConfigForm } from './ConfigForm';
import { MarkdownEditor } from './MarkdownEditor';
import { MarkdownViewer } from './MarkdownViewer';
import { StreamingOutput } from './StreamingOutput';

interface Props {
  run: PipelineRunDetail;
  stage: Stage;
  stageOrder: Stage[];
  registry: StageDefinition[];
  onRefresh: () => void;
  onSelectStage: (stage: Stage) => void;
  getInputArtifacts: (stage: Stage) => Artifact[];
  getStageExecutions: (stage: Stage) => StageExecution[];
}

type OutputTab = 'log' | 'view' | 'edit';

export function StagePanel({
  run,
  stage,
  stageOrder,
  registry,
  onRefresh,
  onSelectStage,
  getInputArtifacts,
  getStageExecutions,
}: Props) {
  const stageDef = registry.find((s) => s.stage === stage);
  const executions = getStageExecutions(stage);
  const inputArtifacts = getInputArtifacts(stage);
  const isRunning = executions.some((e) => e.status === 'running');

  const [selectedSkill, setSelectedSkill] = useState<string>(
    stageDef?.skills[0]?.skill_name ?? '',
  );
  const [outputTab, setOutputTab] = useState<OutputTab>('log');
  const [artifactContent, setArtifactContent] = useState<string>('');
  const [selectedArtifactId, setSelectedArtifactId] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const { stream, startStreaming } = useSSE();

  // Reset selected skill when stage changes
  useEffect(() => {
    setSelectedSkill(stageDef?.skills[0]?.skill_name ?? '');
    setOutputTab('log');
    setArtifactContent('');
    setSelectedArtifactId(null);
  }, [stage, stageDef]);

  // When stream completes, refresh run to get artifacts and switch to view tab
  useEffect(() => {
    if (stream.status === 'complete') {
      onRefresh();
      if (stream.artifactIds.length > 0) {
        setOutputTab('view');
      }
    }
  }, [stream.status, stream.artifactIds, onRefresh]);

  // Load artifact content when we have artifacts and switch to view/edit
  useEffect(() => {
    const stageArtifacts = run.artifacts.filter((a) => a.stage === stage);
    const latest = stageArtifacts[stageArtifacts.length - 1];
    if (latest && (outputTab === 'view' || outputTab === 'edit')) {
      setSelectedArtifactId(latest.id);
      api.getArtifactContent(latest.id).then(setArtifactContent);
    }
  }, [run.artifacts, stage, outputTab]);

  const handleExecute = useCallback(
    async (params: Record<string, string | number | null>, inputArtifactId?: string) => {
      const execution = await api.executeStage({
        pipeline_run_id: run.id,
        stage,
        skill_name: selectedSkill,
        params,
        input_artifact_id: inputArtifactId ?? null,
      });
      setOutputTab('log');
      startStreaming(execution.id);
    },
    [run.id, stage, selectedSkill, startStreaming],
  );

  const handleSaveArtifact = useCallback(
    async (content: string) => {
      if (!selectedArtifactId) return;
      setIsSaving(true);
      await api.updateArtifactContent(selectedArtifactId, content);
      setArtifactContent(content);
      setIsSaving(false);
    },
    [selectedArtifactId],
  );

  const handlePassToNext = useCallback(() => {
    const idx = stageOrder.indexOf(stage);
    if (idx < stageOrder.length - 1) {
      onSelectStage(stageOrder[idx + 1]);
    }
  }, [stage, stageOrder, onSelectStage]);

  const skillVariant = stageDef?.skills.find((s) => s.skill_name === selectedSkill);
  const stageArtifacts = run.artifacts.filter((a) => a.stage === stage);
  const hasArtifacts = stageArtifacts.length > 0;
  const nextStage = stageOrder[stageOrder.indexOf(stage) + 1];

  if (!stageDef) {
    return <div className="p-4 text-gray-400">Stage not found in registry</div>;
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {/* Stage header */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800">{stageDef.label}</h2>
        <p className="text-sm text-gray-500">{stageDef.description}</p>
      </div>

      {/* Skill selector */}
      {stageDef.skills.length > 1 && (
        <div className="flex gap-3">
          {stageDef.skills.map((s) => (
            <label key={s.skill_name} className="flex items-center gap-1.5 text-sm cursor-pointer">
              <input
                type="radio"
                name="skill"
                value={s.skill_name}
                checked={selectedSkill === s.skill_name}
                onChange={() => setSelectedSkill(s.skill_name)}
              />
              <span>{s.label}</span>
            </label>
          ))}
        </div>
      )}

      {/* Config form */}
      {skillVariant && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-3">Configuration</h3>
          <ConfigForm
            key={`${stage}-${selectedSkill}`}
            skillVariant={skillVariant}
            inputArtifacts={inputArtifacts}
            onExecute={handleExecute}
            isRunning={isRunning || stream.status === 'streaming'}
            carryForward={run.param_memory}
          />
        </div>
      )}

      {/* Output panel */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-2">
          <h3 className="text-sm font-medium text-gray-600">Output</h3>
          <div className="flex gap-1">
            {(['log', 'view', 'edit'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setOutputTab(tab)}
                disabled={tab !== 'log' && !hasArtifacts}
                className={`px-3 py-1 text-xs rounded ${
                  outputTab === tab
                    ? 'bg-gray-800 text-white'
                    : tab !== 'log' && !hasArtifacts
                      ? 'text-gray-300 cursor-not-allowed'
                      : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="p-4">
          {outputTab === 'log' && (
            <StreamingOutput
              log={stream.log}
              status={stream.status}
              errorMessage={stream.errorMessage}
            />
          )}
          {outputTab === 'view' && (
            <MarkdownViewer content={artifactContent} />
          )}
          {outputTab === 'edit' && (
            <MarkdownEditor
              content={artifactContent}
              onSave={handleSaveArtifact}
              isSaving={isSaving}
            />
          )}
        </div>
      </div>

      {/* Cost display */}
      {stream.costUsd != null && (
        <div className="text-xs text-gray-400">
          Cost: ${stream.costUsd.toFixed(4)}
        </div>
      )}

      {/* Pass to next stage */}
      {hasArtifacts && nextStage && (
        <button
          onClick={handlePassToNext}
          className="px-4 py-2 text-sm bg-green-500 text-white rounded hover:bg-green-600"
        >
          Pass to {registry.find((s) => s.stage === nextStage)?.label ?? nextStage} &rarr;
        </button>
      )}
    </div>
  );
}
