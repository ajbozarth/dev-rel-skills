import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.models.database import get_db
from backend.models.schemas import StageExecuteRequest, StageExecutionResponse
from backend.services.agent_runner import cancel_execution, start_execution
from backend.services.output_manager import snapshot_workspace
from backend.services.skill_loader import get_registry

router = APIRouter()


@router.get("/registry")
async def get_stage_registry():
    return get_registry()


@router.post("/execute", response_model=StageExecutionResponse, status_code=202)
async def execute_stage(body: StageExecuteRequest):
    db = await get_db()

    # Validate pipeline run exists
    cursor = await db.execute(
        "SELECT * FROM pipeline_runs WHERE id = ?", (body.pipeline_run_id,)
    )
    run = await cursor.fetchone()
    if not run:
        raise HTTPException(404, "Pipeline run not found")

    workspace_dir = str(settings.workspace_root / body.pipeline_run_id)

    # Resolve input artifact filename if provided
    input_artifact_filename = None
    if body.input_artifact_id:
        art_cursor = await db.execute(
            "SELECT * FROM artifacts WHERE id = ?", (body.input_artifact_id,)
        )
        art = await art_cursor.fetchone()
        if not art:
            raise HTTPException(404, "Input artifact not found")
        input_artifact_filename = art["filename"]
        # For virtual artifacts, write content to a temp file in workspace
        if art["is_virtual"]:
            import os

            temp_path = os.path.join(workspace_dir, art["filename"])
            with open(temp_path, "w") as f:
                f.write(art["content"] or "")

    # Create execution record
    execution_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """INSERT INTO stage_executions
           (id, pipeline_run_id, stage, skill_name, status, params_json,
            input_artifact_id, started_at)
           VALUES (?, ?, ?, ?, 'running', ?, ?, ?)""",
        (
            execution_id,
            body.pipeline_run_id,
            body.stage.value,
            body.skill_name,
            json.dumps(body.params),
            body.input_artifact_id,
            now,
        ),
    )
    await db.commit()

    # Snapshot workspace before execution
    pre_files = snapshot_workspace(workspace_dir)

    # Launch background task
    start_execution(
        execution_id=execution_id,
        pipeline_run_id=body.pipeline_run_id,
        stage=body.stage.value,
        skill_name=body.skill_name,
        params=body.params,
        workspace_dir=workspace_dir,
        input_artifact_filename=input_artifact_filename,
        pre_execution_files=pre_files,
    )

    return StageExecutionResponse(
        id=execution_id,
        pipeline_run_id=body.pipeline_run_id,
        stage=body.stage.value,
        skill_name=body.skill_name,
        status="running",
        params_json=json.dumps(body.params),
        input_artifact_id=body.input_artifact_id,
        output_text=None,
        cost_usd=None,
        error_message=None,
        started_at=now,
        completed_at=None,
    )


@router.get("/{execution_id}", response_model=StageExecutionResponse)
async def get_execution(execution_id: str):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM stage_executions WHERE id = ?", (execution_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(404, "Execution not found")
    return StageExecutionResponse(
        id=row["id"],
        pipeline_run_id=row["pipeline_run_id"],
        stage=row["stage"],
        skill_name=row["skill_name"],
        status=row["status"],
        params_json=row["params_json"],
        input_artifact_id=row["input_artifact_id"],
        output_text=row["output_text"],
        cost_usd=row["cost_usd"],
        error_message=row["error_message"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
    )


@router.post("/{execution_id}/cancel")
async def cancel_stage(execution_id: str):
    success = cancel_execution(execution_id)
    if not success:
        raise HTTPException(400, "Execution is not running or not found")
    return {"status": "cancelled"}
