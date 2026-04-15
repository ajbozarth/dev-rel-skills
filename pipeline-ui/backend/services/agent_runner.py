import asyncio
import logging
from datetime import datetime, timezone

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
)

from backend.models.database import get_db
from backend.services.output_manager import detect_and_register_artifacts
from backend.services.pipeline_state import update_pipeline_stage
from backend.services.skill_loader import get_skill_content

logger = logging.getLogger(__name__)

# Active execution queues: execution_id -> asyncio.Queue
_streams: dict[str, asyncio.Queue] = {}
# Active tasks for cancellation: execution_id -> asyncio.Task
_tasks: dict[str, asyncio.Task] = {}


def get_stream(execution_id: str) -> asyncio.Queue | None:
    return _streams.get(execution_id)


def _build_prompt(
    skill_name: str,
    params: dict,
    input_artifact_filename: str | None,
) -> str:
    skill_md = get_skill_content(skill_name)

    param_parts = []
    for key, value in params.items():
        if value is not None and key != "file":
            param_parts.append(f"--{key} {value}")

    file_param = params.get("file")

    prompt = f"""Follow the instructions below to execute the `{skill_name}` skill.

=== SKILL INSTRUCTIONS ===
{skill_md}
=== END SKILL INSTRUCTIONS ===

Execute this skill now with these parameters: /{skill_name} {' '.join(param_parts)}
"""

    filename = file_param or input_artifact_filename
    if filename:
        prompt += f"""
The input file from a previous stage is at: {filename}
(It is already present in the working directory.)
"""

    return prompt


def _summarize_tool_input(block: ToolUseBlock) -> str:
    input_data = block.input if hasattr(block, "input") else {}
    if block.name == "Write":
        return f"Writing {input_data.get('file_path', '?')}"
    elif block.name == "Read":
        return f"Reading {input_data.get('file_path', '?')}"
    elif block.name == "Bash":
        cmd = input_data.get("command", "?")
        return f"$ {cmd[:80]}{'...' if len(str(cmd)) > 80 else ''}"
    elif block.name == "WebFetch":
        return f"Fetching {input_data.get('url', '?')}"
    elif block.name == "Edit":
        return f"Editing {input_data.get('file_path', '?')}"
    elif block.name in ("Glob", "Grep"):
        return f"{block.name}: {input_data.get('pattern', '?')}"
    return f"{block.name}"


async def run_execution(
    execution_id: str,
    pipeline_run_id: str,
    stage: str,
    skill_name: str,
    params: dict,
    workspace_dir: str,
    input_artifact_filename: str | None,
    pre_execution_files: set[str],
) -> None:
    queue = asyncio.Queue()
    _streams[execution_id] = queue

    prompt = _build_prompt(skill_name, params, input_artifact_filename)
    total_cost: float | None = None

    try:
        options = ClaudeAgentOptions(
            cwd=workspace_dir,
            allowed_tools=["Read", "Write", "Edit", "Bash", "WebFetch", "Glob", "Grep"],
            permission_mode="acceptEdits",
            max_turns=30,
        )

        full_text = ""

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            full_text += block.text
                            await queue.put({
                                "event": "text",
                                "data": {"text": block.text},
                            })
                        elif isinstance(block, ToolUseBlock):
                            await queue.put({
                                "event": "tool_use",
                                "data": {
                                    "tool": block.name,
                                    "input_summary": _summarize_tool_input(block),
                                },
                            })
                        elif isinstance(block, ToolResultBlock):
                            content_str = str(block.content) if block.content else ""
                            await queue.put({
                                "event": "tool_result",
                                "data": {
                                    "tool_use_id": block.tool_use_id,
                                    "truncated_output": content_str[:500],
                                },
                            })
                        elif isinstance(block, ThinkingBlock):
                            await queue.put({
                                "event": "thinking",
                                "data": {"text": block.thinking},
                            })
                elif isinstance(message, ResultMessage):
                    total_cost = message.total_cost_usd

        # Execution completed — detect artifacts and update DB
        artifact_ids = await detect_and_register_artifacts(
            execution_id, pipeline_run_id, stage, skill_name,
            workspace_dir, pre_execution_files, full_text,
        )

        db = await get_db()
        await db.execute(
            "UPDATE stage_executions SET status='completed', output_text=?, cost_usd=?, completed_at=? WHERE id=?",
            (full_text, total_cost, datetime.now(timezone.utc).isoformat(), execution_id),
        )
        await db.commit()
        await update_pipeline_stage(pipeline_run_id, stage)

        await queue.put({
            "event": "complete",
            "data": {
                "artifact_ids": artifact_ids,
                "output_text_length": len(full_text),
                "cost_usd": total_cost,
            },
        })

    except asyncio.CancelledError:
        db = await get_db()
        await db.execute(
            "UPDATE stage_executions SET status='cancelled', completed_at=? WHERE id=?",
            (datetime.now(timezone.utc).isoformat(), execution_id),
        )
        await db.commit()
        await queue.put({"event": "error", "data": {"message": "Execution cancelled"}})
        raise
    except Exception as e:
        logger.exception("Execution %s failed", execution_id)
        db = await get_db()
        await db.execute(
            "UPDATE stage_executions SET status='failed', error_message=?, completed_at=? WHERE id=?",
            (str(e), datetime.now(timezone.utc).isoformat(), execution_id),
        )
        await db.commit()
        await queue.put({"event": "error", "data": {"message": str(e)}})
    finally:
        _tasks.pop(execution_id, None)


def start_execution(execution_id: str, **kwargs) -> None:
    task = asyncio.create_task(run_execution(execution_id, **kwargs))
    _tasks[execution_id] = task


def cancel_execution(execution_id: str) -> bool:
    task = _tasks.get(execution_id)
    if task and not task.done():
        task.cancel()
        return True
    return False


def cleanup_stream(execution_id: str) -> None:
    _streams.pop(execution_id, None)
