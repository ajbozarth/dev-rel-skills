import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import type { Artifact, PipelineRun, PipelineRunDetail, Stage, StageDefinition, StageExecution } from '../types';

export function usePipeline() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [activeRun, setActiveRun] = useState<PipelineRunDetail | null>(null);
  const [registry, setRegistry] = useState<StageDefinition[]>([]);
  const [selectedStage, setSelectedStage] = useState<Stage>('scout');

  // Load registry once
  useEffect(() => {
    api.getRegistry().then(setRegistry);
  }, []);

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

  const createRun = useCallback(async (name: string, repo?: string) => {
    const run = await api.createRun(name, repo);
    setRuns((prev) => [run, ...prev]);
    setActiveRunId(run.id);
  }, []);

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

  return {
    runs,
    activeRunId,
    activeRun,
    registry,
    selectedStage,
    setActiveRunId,
    createRun,
    refreshRun,
    deleteRun,
    selectStage,
    getStageExecutions,
    getInputArtifacts,
  };
}
