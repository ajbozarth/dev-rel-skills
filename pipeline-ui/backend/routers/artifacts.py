from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from backend.models.database import get_db
from backend.models.schemas import ArtifactContentUpdate, ArtifactResponse

router = APIRouter()


@router.get("", response_model=list[ArtifactResponse])
async def list_artifacts(pipeline_run_id: str):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM artifacts WHERE pipeline_run_id = ? ORDER BY created_at",
        (pipeline_run_id,),
    )
    rows = await cursor.fetchall()
    return [
        ArtifactResponse(
            id=r["id"],
            execution_id=r["execution_id"],
            pipeline_run_id=r["pipeline_run_id"],
            stage=r["stage"],
            filename=r["filename"],
            content=None,
            file_path=r["file_path"],
            is_virtual=bool(r["is_virtual"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.get("/{artifact_id}/content")
async def get_artifact_content(artifact_id: str):
    db = await get_db()
    cursor = await db.execute(
        "SELECT content FROM artifacts WHERE id = ?", (artifact_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(404, "Artifact not found")
    return PlainTextResponse(row["content"] or "", media_type="text/markdown")


@router.put("/{artifact_id}/content", status_code=204)
async def update_artifact_content(artifact_id: str, body: ArtifactContentUpdate):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM artifacts WHERE id = ?", (artifact_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(404, "Artifact not found")

    await db.execute(
        "UPDATE artifacts SET content = ? WHERE id = ?",
        (body.content, artifact_id),
    )
    await db.commit()

    # Also write to disk if this artifact has a file path
    if row["file_path"]:
        Path(row["file_path"]).write_text(body.content)
