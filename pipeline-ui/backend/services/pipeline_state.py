from datetime import datetime, timezone

from backend.models.database import get_db

STAGE_ORDER = ["scout", "discover", "draft", "validate", "polish", "preview", "promote"]


async def update_pipeline_stage(pipeline_run_id: str, completed_stage: str) -> None:
    """After a stage completes successfully, update the run's current_stage."""
    db = await get_db()
    await db.execute(
        "UPDATE pipeline_runs SET current_stage = ?, updated_at = ? WHERE id = ?",
        (completed_stage, datetime.now(timezone.utc).isoformat(), pipeline_run_id),
    )
    await db.commit()
