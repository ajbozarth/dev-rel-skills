import asyncio
import json

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from backend.services.agent_runner import cleanup_stream, get_stream

router = APIRouter()


@router.get("/{execution_id}")
async def stream_execution(execution_id: str):
    queue = get_stream(execution_id)
    if queue is None:
        raise HTTPException(404, "No active stream for this execution")

    async def event_generator():
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=300.0)
                yield {
                    "event": event["event"],
                    "data": json.dumps(event["data"]),
                }
                if event["event"] in ("complete", "error"):
                    break
        except asyncio.TimeoutError:
            yield {
                "event": "error",
                "data": json.dumps({"message": "Stream timed out after 5 minutes of silence"}),
            }
        finally:
            cleanup_stream(execution_id)

    return EventSourceResponse(event_generator())
