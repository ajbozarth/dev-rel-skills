import type {
  Artifact,
  PipelineRun,
  PipelineRunDetail,
  PipelineType,
  PipelineTypeDef,
  StageDefinition,
  StageExecution,
  StageExecuteRequest,
} from '../types';

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  // Pipeline Runs
  createRun: (name: string, repo_context?: string, pipeline_type: PipelineType = 'content') =>
    request<PipelineRun>('/pipelines', {
      method: 'POST',
      body: JSON.stringify({ name, repo_context, pipeline_type }),
    }),
  listRuns: () => request<PipelineRun[]>('/pipelines'),
  getRun: (id: string) => request<PipelineRunDetail>(`/pipelines/${id}`),
  deleteRun: (id: string) => request<void>(`/pipelines/${id}`, { method: 'DELETE' }),

  // Stages
  getPipelineTypes: () => request<PipelineTypeDef[]>('/stages/pipeline-types'),
  getRegistry: (pipelineType?: string) =>
    request<StageDefinition[]>(
      `/stages/registry${pipelineType ? `?pipeline_type=${pipelineType}` : ''}`,
    ),
  executeStage: (body: StageExecuteRequest) =>
    request<StageExecution>('/stages/execute', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  getExecution: (id: string) => request<StageExecution>(`/stages/${id}`),
  cancelExecution: (id: string) =>
    request<void>(`/stages/${id}/cancel`, { method: 'POST' }),

  // Artifacts
  listArtifacts: (runId: string) =>
    request<Artifact[]>(`/artifacts?pipeline_run_id=${runId}`),
  getArtifactContent: (id: string) =>
    fetch(`${BASE}/artifacts/${id}/content`).then((r) => r.text()),
  updateArtifactContent: (id: string, content: string) =>
    request<void>(`/artifacts/${id}/content`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    }),
};
