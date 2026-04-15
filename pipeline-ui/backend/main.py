import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.models.database import close_db, init_db
from backend.routers import artifacts, pipelines, stages, stream
from backend.services.skill_loader import get_registry, load_skills


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.workspace_root.mkdir(parents=True, exist_ok=True)
    await init_db(settings.db_path)
    load_skills()
    yield
    await close_db()


app = FastAPI(title="Dev-Rel Pipeline UI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipelines.router, prefix="/api/pipelines", tags=["pipelines"])
app.include_router(stages.router, prefix="/api/stages", tags=["stages"])
app.include_router(stream.router, prefix="/api/stream", tags=["stream"])
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["artifacts"])


@app.get("/api/health")
async def health():
    gh_available = shutil.which("gh") is not None
    return {
        "status": "ok",
        "gh_cli": gh_available,
        "skills_loaded": len(get_registry()),
    }
