# Pipeline UI

Web interface for the dev-rel content pipeline. Runs the repo's 9 Claude Code skills through a visual 7-stage workflow — Scout, Discover, Draft, Validate, Polish, Preview, Promote — with real-time streaming output, inline editing, and artifact passing between stages.

```
Browser (React + TS)          FastAPI Backend              Claude Agent SDK
─────────────────────         ──────────────               ─────────────────
PipelineBar                   POST /api/stages/execute  →  Read SKILL.md
StagePanel + ConfigForm       GET  /api/stream/{id}  ←──  Stream agent output (SSE)
StreamingOutput / Editor      GET  /api/artifacts/{id}     Output files on disk
MarkdownViewer                SQLite (runs, executions,
ArtifactPicker                       artifacts)
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [gh](https://cli.github.com/) CLI, authenticated (`gh auth login`)
- Claude Code CLI installed (provides the `claude-agent-sdk` runtime)

## Quick Start

```bash
# Install dependencies
cd pipeline-ui
uv sync
cd frontend && npm install && cd ..

# Start backend (terminal 1)
uv run uvicorn backend.main:app --reload --port 8000

# Start frontend (terminal 2)
cd frontend && npm run dev
```

Open http://localhost:5173.

## Usage

1. **Create a pipeline run** — click **+** in the sidebar, give it a name and optional `owner/repo` context.
2. **Select a stage** — click any stage chip in the pipeline bar (Scout, Discover, Draft, etc.).
3. **Choose a skill variant** — stages with multiple skills (e.g., Scout has "HN Scout" and "HN Scout (generic)") show radio buttons.
4. **Configure parameters** — fill in the form. Stages that take input from a previous stage show an artifact picker dropdown.
5. **Run** — click "Run Stage". Output streams in real time in the Log tab.
6. **Review** — switch to the **View** tab to see rendered markdown, or **Edit** to tweak the output in a CodeMirror editor. Edits save to both the database and disk.
7. **Pass forward** — click "Pass to [Next Stage]" to advance the pipeline with the current output as input.

## Pipeline Stages

| Stage | Skills | What it does |
|-------|--------|-------------|
| Scout | `hn-scout`, `hn-scout-generic` | Scan Hacker News for trending topics with demo potential |
| Discover | `get-blog-candidates` | Rank merged PRs by blog-worthiness |
| Draft | `release-blog`, `write-technical-blog` | Write blog post drafts |
| Validate | `validate-snippets` | Execute code blocks in a draft and report pass/fail |
| Polish | `de-llmify` | Remove LLM writing patterns |
| Preview | `link-preview` | Generate link card, Open Graph tags, Twitter Card |
| Promote | `write-tweet` | Write tweet threads for the finished post |

Stages can be run independently or in any order. The pipeline bar tracks which stages have been completed for each run.

## Project Structure

```
pipeline-ui/
├── pyproject.toml              # Python deps (FastAPI, claude-agent-sdk, aiosqlite, sse-starlette)
├── backend/
│   ├── main.py                 # FastAPI app, CORS, lifespan
│   ├── config.py               # Paths: skills dir, workspace root, DB
│   ├── models/
│   │   ├── database.py         # SQLite schema + aiosqlite connection
│   │   └── schemas.py          # Pydantic request/response models
│   ├── routers/
│   │   ├── pipelines.py        # CRUD for pipeline runs
│   │   ├── stages.py           # Execute stage, get status, cancel
│   │   ├── stream.py           # SSE endpoint
│   │   └── artifacts.py        # Serve + update output files
│   └── services/
│       ├── skill_loader.py     # Reads SKILL.md files, builds stage registry
│       ├── agent_runner.py     # Runs skills via claude-agent-sdk, streams events
│       ├── output_manager.py   # Detects output files, registers artifacts
│       └── pipeline_state.py   # Run lifecycle tracking
├── frontend/
│   ├── package.json            # React 19, Vite, Tailwind, CodeMirror, react-markdown
│   └── src/
│       ├── api/                # Typed fetch wrapper + SSE EventSource wrapper
│       ├── hooks/              # usePipeline (state), useSSE (streaming)
│       ├── components/         # RunsSidebar, PipelineBar, StagePanel, ConfigForm,
│       │                       # ArtifactPicker, StreamingOutput, MarkdownViewer,
│       │                       # MarkdownEditor
│       └── types/              # TypeScript types matching backend schemas
└── workspace/                  # Created at runtime, gitignored
    └── pipelines/{run_id}/     # Shared working directory per run
```

## API

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/health` | Health check (returns `gh` CLI status + skill count) |
| `POST` | `/api/pipelines` | Create a pipeline run |
| `GET` | `/api/pipelines` | List all runs |
| `GET` | `/api/pipelines/{id}` | Get run with executions + artifacts |
| `DELETE` | `/api/pipelines/{id}` | Delete run + workspace |
| `GET` | `/api/stages/registry` | Stage definitions with skill variants + parameter schemas |
| `POST` | `/api/stages/execute` | Start a stage execution |
| `GET` | `/api/stages/{id}` | Execution status |
| `POST` | `/api/stages/{id}/cancel` | Cancel running execution |
| `GET` | `/api/stream/{id}` | SSE stream of agent output (events: `text`, `tool_use`, `tool_result`, `thinking`, `complete`, `error`) |
| `GET` | `/api/artifacts?pipeline_run_id=X` | List artifacts for a run |
| `GET` | `/api/artifacts/{id}/content` | Raw markdown content |
| `PUT` | `/api/artifacts/{id}/content` | Update content (writes to DB + file on disk) |

## How Artifacts Pass Between Stages

Each pipeline run gets a shared workspace directory (`workspace/pipelines/{run_id}/`). When a stage completes, the backend scans the workspace for new `.md` files and registers them as artifacts. When you run a subsequent stage with an artifact as input, the backend includes the filename in the agent's prompt — the file is already in the shared workspace, so the agent reads it directly.

Three artifact types are handled:
- **File output** (most skills) — new `.md` files detected in workspace after execution
- **Text output** (`get-blog-candidates`) — agent text stored as a virtual artifact, written to disk on demand
- **Overwrite** (`de-llmify`) — overwrites the input file in place; a new artifact record is created while the original is preserved in the database
