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
    StageExecutionResponse,
)

router = APIRouter()


@router.post("", response_model=PipelineRunResponse, status_code=201)
async def create_pipeline_run(body: PipelineRunCreate):
    db = await get_db()
    run_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    workspace_dir = settings.workspace_root / run_id
    workspace_dir.mkdir(parents=True, exist_ok=True)

    await db.execute(
        "INSERT INTO pipeline_runs (id, name, repo_context, current_stage, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (run_id, body.name, body.repo_context, None, now, now),
    )
    await db.commit()

    return PipelineRunResponse(
        id=run_id,
        name=body.name,
        repo_context=body.repo_context,
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

    return PipelineRunDetail(
        id=run["id"],
        name=run["name"],
        repo_context=run["repo_context"],
        current_stage=run["current_stage"],
        created_at=run["created_at"],
        updated_at=run["updated_at"],
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
