export type Stage = 'scout' | 'discover' | 'draft' | 'validate' | 'polish' | 'preview' | 'promote';
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface ParamDef {
  name: string;
  label: string;
  type: 'integer' | 'string' | 'date' | 'artifact';
  required: boolean;
  default?: string | number | null;
  description: string;
}

export interface SkillVariant {
  skill_name: string;
  label: string;
  description: string;
  params: ParamDef[];
  output_pattern: string;
  output_type: 'file' | 'text' | 'overwrite';
}

export interface StageDefinition {
  stage: Stage;
  label: string;
  description: string;
  skills: SkillVariant[];
  accepts_input: boolean;
  input_from_stages: Stage[];
}

export interface PipelineRun {
  id: string;
  name: string;
  repo_context: string | null;
  current_stage: string | null;
  created_at: string;
  updated_at: string;
}

export interface PipelineRunDetail extends PipelineRun {
  executions: StageExecution[];
  artifacts: Artifact[];
}

export interface StageExecution {
  id: string;
  pipeline_run_id: string;
  stage: Stage;
  skill_name: string;
  status: ExecutionStatus;
  params_json: string | null;
  input_artifact_id: string | null;
  output_text: string | null;
  cost_usd: number | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface Artifact {
  id: string;
  execution_id: string;
  pipeline_run_id: string;
  stage: Stage;
  filename: string;
  content: string | null;
  file_path: string | null;
  is_virtual: boolean;
  created_at: string;
}

export interface StageExecuteRequest {
  pipeline_run_id: string;
  stage: Stage;
  skill_name: string;
  params: Record<string, string | number | null>;
  input_artifact_id?: string | null;
}

export interface SSETextEvent { text: string }
export interface SSEToolUseEvent { tool: string; input_summary: string }
export interface SSEToolResultEvent { tool_use_id: string; truncated_output: string }
export interface SSEThinkingEvent { text: string }
export interface SSECompleteEvent { artifact_ids: string[]; output_text_length: number; cost_usd: number | null }
export interface SSEErrorEvent { message: string }
