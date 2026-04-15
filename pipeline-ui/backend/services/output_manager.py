from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.models.database import get_db
from backend.services.skill_loader import get_skill_variant


async def detect_and_register_artifacts(
    execution_id: str,
    pipeline_run_id: str,
    stage: str,
    skill_name: str,
    workspace_dir: str,
    pre_execution_files: set[str],
    agent_output_text: str,
) -> list[str]:
    """Scan workspace for new/modified files after execution. Register as artifacts.
    Returns list of artifact IDs created."""
    db = await get_db()
    artifact_ids = []
    skill_variant = get_skill_variant(stage, skill_name)

    if skill_variant and skill_variant.output_type == "text":
        # get-blog-candidates: no file output, store agent text as virtual artifact
        art_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        await db.execute(
            "INSERT INTO artifacts (id, execution_id, pipeline_run_id, stage, filename, content, file_path, is_virtual, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (art_id, execution_id, pipeline_run_id, stage, f"{skill_name}-output.md", agent_output_text, None, 1, now),
        )
        artifact_ids.append(art_id)

    elif skill_variant and skill_variant.output_type == "overwrite":
        # de-llmify: overwrites input file in place
        cursor = await db.execute(
            "SELECT input_artifact_id FROM stage_executions WHERE id = ?",
            (execution_id,),
        )
        result = await cursor.fetchone()
        if result and result["input_artifact_id"]:
            art_cursor = await db.execute(
                "SELECT * FROM artifacts WHERE id = ?",
                (result["input_artifact_id"],),
            )
            input_art = await art_cursor.fetchone()
            if input_art and input_art["file_path"]:
                fp = Path(input_art["file_path"])
                if fp.exists():
                    new_content = fp.read_text()
                    art_id = str(uuid4())
                    now = datetime.now(timezone.utc).isoformat()
                    await db.execute(
                        "INSERT INTO artifacts (id, execution_id, pipeline_run_id, stage, filename, content, file_path, is_virtual, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (art_id, execution_id, pipeline_run_id, stage, input_art["filename"], new_content, input_art["file_path"], 0, now),
                    )
                    artifact_ids.append(art_id)

    else:
        # Standard file output: scan for new files
        current_files = set()
        wd = Path(workspace_dir)
        if wd.exists():
            for f in wd.iterdir():
                if f.is_file():
                    current_files.add(str(f))

        new_files = current_files - pre_execution_files

        for fpath in sorted(new_files):
            p = Path(fpath)
            if p.suffix == ".md":
                content = p.read_text()
                art_id = str(uuid4())
                now = datetime.now(timezone.utc).isoformat()
                await db.execute(
                    "INSERT INTO artifacts (id, execution_id, pipeline_run_id, stage, filename, content, file_path, is_virtual, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (art_id, execution_id, pipeline_run_id, stage, p.name, content, str(p), 0, now),
                )
                artifact_ids.append(art_id)

    await db.commit()
    return artifact_ids


def snapshot_workspace(workspace_dir: str) -> set[str]:
    """Return the set of file paths currently in the workspace. Called before execution."""
    result = set()
    wd = Path(workspace_dir)
    if wd.exists():
        for f in wd.iterdir():
            if f.is_file():
                result.add(str(f))
    return result
