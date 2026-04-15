import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import type {
  Artifact,
  PipelineRun,
  PipelineRunDetail,
  PipelineType,
  PipelineTypeDef,
  Stage,
  StageDefinition,
  StageExecution,
} from '../types';

export function usePipeline() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [activeRun, setActiveRun] = useState<PipelineRunDetail | null>(null);
  const [registry, setRegistry] = useState<StageDefinition[]>([]);
  const [pipelineTypes, setPipelineTypes] = useState<PipelineTypeDef[]>([]);
  const [selectedStage, setSelectedStage] = useState<Stage>('scout');

  // Derive stage order from the registry (no more hardcoded constant)
  const stageOrder = useMemo<Stage[]>(
    () => registry.map((s) => s.stage),
    [registry],
  );

  // Load pipeline types once
  useEffect(() => {
    api.getPipelineTypes().then(setPipelineTypes);
  }, []);

  // Load registry filtered by active run's pipeline type
  useEffect(() => {
    const pipelineType = activeRun?.pipeline_type;
    api.getRegistry(pipelineType).then((reg) => {
      setRegistry(reg);
    });
  }, [activeRun?.pipeline_type]);

  // Reset selected stage to first in pipeline when registry changes
  useEffect(() => {
    if (stageOrder.length > 0 && !stageOrder.includes(selectedStage)) {
      setSelectedStage(stageOrder[0]);
    }
  }, [stageOrder, selectedStage]);

  // Load runs on mount
  useEffect(() => {
    api.listRuns().then(setRuns);
  }, []);

  // When activeRunId changes, fetch full detail
  useEffect(() => {
    if (activeRunId) {
      api.getRun(activeRunId).then(setActiveRun);
    } else {
      setActiveRun(null);
    }
  }, [activeRunId]);

  const createRun = useCallback(
    async (name: string, repo?: string, pipelineType: PipelineType = 'feature_blog') => {
      const run = await api.createRun(name, repo, pipelineType);
      setRuns((prev) => [run, ...prev]);
      setActiveRunId(run.id);
    },
    [],
  );

  const refreshRun = useCallback(async () => {
    if (activeRunId) {
      const run = await api.getRun(activeRunId);
      setActiveRun(run);
    }
  }, [activeRunId]);

  const deleteRun = useCallback(async (id: string) => {
    await api.deleteRun(id);
    setRuns((prev) => prev.filter((r) => r.id !== id));
    if (activeRunId === id) {
      setActiveRunId(null);
    }
  }, [activeRunId]);

  const selectStage = useCallback((stage: Stage) => {
    setSelectedStage(stage);
  }, []);

  const getStageExecutions = useCallback(
    (stage: Stage): StageExecution[] => {
      return activeRun?.executions.filter((e) => e.stage === stage) ?? [];
    },
    [activeRun],
  );

  const getInputArtifacts = useCallback(
    (stage: Stage): Artifact[] => {
      const stageDef = registry.find((s) => s.stage === stage);
      if (!stageDef) return [];
      return (
        activeRun?.artifacts.filter((a) =>
          stageDef.input_from_stages.includes(a.stage),
        ) ?? []
      );
    },
    [activeRun, registry],
  );

  // Research status for runs with auto-triggered project research
  const researchStatus = useMemo(() => {
    if (!activeRun) return null;
    const contextExecs = activeRun.executions.filter((e) => e.stage === 'context');
    if (contextExecs.length === 0) return null;
    const latest = contextExecs[contextExecs.length - 1];
    return latest.status;
  }, [activeRun]);

  return {
    runs,
    activeRunId,
    activeRun,
    registry,
    stageOrder,
    pipelineTypes,
    selectedStage,
    researchStatus,
    setActiveRunId,
    createRun,
    refreshRun,
    deleteRun,
    selectStage,
    getStageExecutions,
    getInputArtifacts,
  };
}
