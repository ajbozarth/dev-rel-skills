from pathlib import Path

import aiosqlite

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    repo_context TEXT,
    pipeline_type TEXT NOT NULL DEFAULT 'feature_blog',
    current_stage TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stage_executions (
    id TEXT PRIMARY KEY,
    pipeline_run_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    params_json TEXT,
    input_artifact_id TEXT,
    output_text TEXT,
    cost_usd REAL,
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (pipeline_run_id) REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (input_artifact_id) REFERENCES artifacts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    pipeline_run_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    filename TEXT NOT NULL,
    content TEXT,
    file_path TEXT,
    is_virtual INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
"""

_db: aiosqlite.Connection | None = None


async def init_db(db_path: Path) -> None:
    global _db
    _db = await aiosqlite.connect(str(db_path))
    _db.row_factory = aiosqlite.Row
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA foreign_keys=ON")
    await _db.executescript(SCHEMA_SQL)

    # Migration: add pipeline_type column if missing (for existing databases)
    cursor = await _db.execute("PRAGMA table_info(pipeline_runs)")
    columns = {row[1] for row in await cursor.fetchall()}
    if "pipeline_type" not in columns:
        await _db.execute(
            "ALTER TABLE pipeline_runs ADD COLUMN pipeline_type TEXT NOT NULL DEFAULT 'feature_blog'"
        )

    # Migration: rename 'content' pipeline type to 'feature_blog'
    await _db.execute(
        "UPDATE pipeline_runs SET pipeline_type = 'feature_blog' WHERE pipeline_type = 'content'"
    )

    await _db.commit()


async def get_db() -> aiosqlite.Connection:
    assert _db is not None, "Database not initialized"
    return _db


async def close_db() -> None:
    global _db
    if _db:
        await _db.close()
        _db = None
