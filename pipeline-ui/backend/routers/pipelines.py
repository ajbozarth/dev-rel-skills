import json
import shutil
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.models.database import get_db
from backend.models.schemas import (
    ArtifactResponse,
    PipelineRunCreate,
    PipelineRunDetail,
    PipelineRunResponse,
    PipelineTypeEnum,
    StageExecutionResponse,
)
from backend.services.agent_runner import start_execution
from backend.services.output_manager import snapshot_workspace
from backend.services.skill_loader import get_skill_content

router = APIRouter()

_AUTO_RESEARCH_TYPES = {
    PipelineTypeEnum.release_blog,
    PipelineTypeEnum.feature_blog,
    PipelineTypeEnum.topical_blog,
}


@router.post("", response_model=PipelineRunResponse, status_code=201)
async def create_pipeline_run(body: PipelineRunCreate):
    db = await get_db()
    run_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    workspace_dir = settings.workspace_root / run_id
    workspace_dir.mkdir(parents=True, exist_ok=True)

    await db.execute(
        "INSERT INTO pipeline_runs (id, name, repo_context, pipeline_type, current_stage, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (run_id, body.name, body.repo_context, body.pipeline_type.value, None, now, now),
    )
    await db.commit()

    # Auto-trigger project research for runs with a repo
    if body.pipeline_type in _AUTO_RESEARCH_TYPES and body.repo_context:
        try:
            # Verify the skill exists (load_skills must have found it)
            get_skill_content("research-project")

            execution_id = str(uuid4())
            await db.execute(
                """INSERT INTO stage_executions
                   (id, pipeline_run_id, stage, skill_name, status, params_json,
                    input_artifact_id, started_at)
                   VALUES (?, ?, ?, ?, 'running', ?, ?, ?)""",
                (
                    execution_id,
                    run_id,
                    "context",
                    "research-project",
                    json.dumps({"repo": body.repo_context}),
                    None,
                    now,
                ),
            )
            await db.commit()

            pre_files = snapshot_workspace(str(workspace_dir))
            start_execution(
                execution_id=execution_id,
                pipeline_run_id=run_id,
                stage="context",
                skill_name="research-project",
                params={"repo": body.repo_context},
                workspace_dir=str(workspace_dir),
                input_artifact_filename=None,
                pre_execution_files=pre_files,
            )
        except KeyError:
            pass  # research-project skill not installed, skip silently

    return PipelineRunResponse(
        id=run_id,
        name=body.name,
        repo_context=body.repo_context,
        pipeline_type=body.pipeline_type.value,
        current_stage=None,
        created_at=now,
        updated_at=now,
    )


@router.get("", response_model=list[PipelineRunResponse])
async def list_pipeline_runs():
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM pipeline_runs ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [
        PipelineRunResponse(
            id=r["id"],
            name=r["name"],
            repo_context=r["repo_context"],
            pipeline_type=r["pipeline_type"],
            current_stage=r["current_stage"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in rows
    ]


@router.get("/{run_id}", response_model=PipelineRunDetail)
async def get_pipeline_run(run_id: str):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM pipeline_runs WHERE id = ?", (run_id,)
    )
    run = await cursor.fetchone()
    if not run:
        raise HTTPException(404, "Pipeline run not found")

    exec_cursor = await db.execute(
        "SELECT * FROM stage_executions WHERE pipeline_run_id = ? ORDER BY started_at",
        (run_id,),
    )
    executions = await exec_cursor.fetchall()

    art_cursor = await db.execute(
        "SELECT * FROM artifacts WHERE pipeline_run_id = ? ORDER BY created_at",
        (run_id,),
    )
    artifacts = await art_cursor.fetchall()

    # Build param memory: merge params from all completed executions
    param_memory: dict[str, str | int | None] = {}
    if run["repo_context"]:
        param_memory["repo"] = run["repo_context"]
    for e in executions:
        if e["status"] == "completed" and e["params_json"]:
            try:
                params = json.loads(e["params_json"])
                for k, v in params.items():
                    if v is not None:
                        param_memory[k] = v
            except (json.JSONDecodeError, TypeError):
                pass

    return PipelineRunDetail(
        id=run["id"],
        name=run["name"],
        repo_context=run["repo_context"],
        pipeline_type=run["pipeline_type"],
        current_stage=run["current_stage"],
        created_at=run["created_at"],
        updated_at=run["updated_at"],
        param_memory=param_memory,
        executions=[
            StageExecutionResponse(
                id=e["id"],
                pipeline_run_id=e["pipeline_run_id"],
                stage=e["stage"],
                skill_name=e["skill_name"],
                status=e["status"],
                params_json=e["params_json"],
                input_artifact_id=e["input_artifact_id"],
                output_text=e["output_text"],
                cost_usd=e["cost_usd"],
                error_message=e["error_message"],
                started_at=e["started_at"],
                completed_at=e["completed_at"],
            )
            for e in executions
        ],
        artifacts=[
            ArtifactResponse(
                id=a["id"],
                execution_id=a["execution_id"],
                pipeline_run_id=a["pipeline_run_id"],
                stage=a["stage"],
                filename=a["filename"],
                content=None,  # omit content in list view
                file_path=a["file_path"],
                is_virtual=bool(a["is_virtual"]),
                created_at=a["created_at"],
            )
            for a in artifacts
        ],
    )


@router.delete("/{run_id}", status_code=204)
async def delete_pipeline_run(run_id: str):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM pipeline_runs WHERE id = ?", (run_id,)
    )
    run = await cursor.fetchone()
    if not run:
        raise HTTPException(404, "Pipeline run not found")

    await db.execute("DELETE FROM artifacts WHERE pipeline_run_id = ?", (run_id,))
    await db.execute(
        "DELETE FROM stage_executions WHERE pipeline_run_id = ?", (run_id,)
    )
    await db.execute("DELETE FROM pipeline_runs WHERE id = ?", (run_id,))
    await db.commit()

    workspace_dir = settings.workspace_root / run_id
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)
