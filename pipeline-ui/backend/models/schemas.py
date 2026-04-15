from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class StageEnum(str, Enum):
    scout = "scout"
    discover = "discover"
    draft = "draft"
    validate = "validate"
    polish = "polish"
    preview = "preview"
    promote = "promote"
    context = "context"  # virtual stage for auto-research artifacts


class PipelineTypeEnum(str, Enum):
    feature_blog = "feature_blog"
    release_blog = "release_blog"
    topical_blog = "topical_blog"


class ExecutionStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


# --- Stage Registry ---


class ParamDef(BaseModel):
    name: str
    label: str
    type: str  # "integer" | "string" | "date" | "artifact"
    required: bool = False
    default: str | int | None = None
    description: str = ""


class SkillVariant(BaseModel):
    skill_name: str
    label: str
    description: str
    params: list[ParamDef]
    output_pattern: str
    output_type: str  # "file" | "text" | "overwrite"


class StageDefinition(BaseModel):
    stage: StageEnum
    label: str
    description: str
    skills: list[SkillVariant]
    accepts_input: bool
    input_from_stages: list[StageEnum] = []


# --- Pipeline Runs ---


class PipelineRunCreate(BaseModel):
    name: str
    repo_context: str | None = None
    pipeline_type: PipelineTypeEnum = PipelineTypeEnum.feature_blog


class PipelineRunResponse(BaseModel):
    id: str
    name: str
    repo_context: str | None
    pipeline_type: str
    current_stage: str | None
    created_at: str
    updated_at: str


class PipelineTypeDefResponse(BaseModel):
    name: str
    label: str
    description: str
    stages: list[str]


class PipelineRunDetail(PipelineRunResponse):
    executions: list[StageExecutionResponse]
    artifacts: list[ArtifactResponse]
    param_memory: dict[str, str | int | None] = {}


# --- Stage Executions ---


class StageExecuteRequest(BaseModel):
    pipeline_run_id: str
    stage: StageEnum
    skill_name: str
    params: dict[str, str | int | None] = {}
    input_artifact_id: str | None = None


class StageExecutionResponse(BaseModel):
    id: str
    pipeline_run_id: str
    stage: str
    skill_name: str
    status: str
    params_json: str | None
    input_artifact_id: str | None
    output_text: str | None
    cost_usd: float | None
    error_message: str | None
    started_at: str | None
    completed_at: str | None


# --- Artifacts ---


class ArtifactResponse(BaseModel):
    id: str
    execution_id: str
    pipeline_run_id: str
    stage: str
    filename: str
    content: str | None = None
    file_path: str | None
    is_virtual: bool
    created_at: str


class ArtifactContentUpdate(BaseModel):
    content: str
