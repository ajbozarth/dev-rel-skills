# Dev-Rel Content Pipeline Web App

## Context

The `dev-rel-skills` repo has 9 Claude Code skills (SKILL.md files) that form a sequential content pipeline: **Scout → Discover → Draft → Validate → Polish → Preview → Promote**. Currently these are invoked manually via `/skill-name` in Claude Code CLI. The goal is to build a web UI that lets a user work through this pipeline visually, with each stage running via the `claude-agent-sdk` Python package behind the scenes, streaming output in real time.

The app will live in `pipeline-ui/` inside this repo.

---

## Architecture

```
Browser (React + TS)          FastAPI Backend              Claude Agent SDK
─────────────────────         ──────────────               ─────────────────
PipelineBar                   POST /api/stages/execute  →  Read SKILL.md
StagePanel + ConfigForm       GET  /api/stream/{id}  ←──  Stream agent output (SSE)
StreamingOutput / Editor      GET  /api/artifacts/{id}     Output files on disk
MarkdownViewer                SQLite (runs, executions,
ArtifactPicker                       artifacts)
```

**Frontend:** React + TypeScript + Vite. Tailwind CSS for styling. `react-markdown` + `rehype-highlight` for rendered output. CodeMirror for inline editing.

**Backend:** FastAPI (Python). `claude-agent-sdk` for running skills. `aiosqlite` for state. SSE for streaming.

**Skill invocation:** Read the SKILL.md content, construct a prompt including the instructions + parameters, send to the Agent SDK's `ClaudeSDKClient`. The agent follows the skill instructions using its built-in tools (Read, Write, Bash, WebFetch, etc.).

**Working directory:** Each pipeline run gets `workspace/pipelines/{run_id}/`. All stages in a run share this directory so inter-stage file references (e.g., validate-snippets reading a blog post) work naturally.

**Concurrency:** Multiple pipeline runs can be active simultaneously. Each run has its own workspace directory and agent sessions.

---

## Directory Structure

```
pipeline-ui/
├── pyproject.toml
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS, lifespan, mount static
│   ├── config.py                # Settings: skills path, workspace root, DB path
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite schema + connection (aiosqlite)
│   │   └── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── pipelines.py         # CRUD for pipeline runs
│   │   ├── stages.py            # Execute stage, get status, cancel
│   │   ├── stream.py            # SSE endpoint
│   │   └── artifacts.py         # Serve + update output files
│   └── services/
│       ├── __init__.py
│       ├── skill_loader.py      # Read SKILL.md files, build stage registry
│       ├── agent_runner.py      # Construct prompts, run via SDK, stream events
│       ├── output_manager.py    # Detect output files, register artifacts
│       └── pipeline_state.py    # Run lifecycle, stage transitions
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx
│       ├── App.tsx               # Layout: sidebar + pipeline bar + stage panel
│       ├── api/
│       │   ├── client.ts         # Typed fetch wrapper
│       │   └── sse.ts            # EventSource wrapper
│       ├── components/
│       │   ├── PipelineBar.tsx   # Horizontal stage indicator
│       │   ├── StagePanel.tsx    # Config form + output for selected stage
│       │   ├── ConfigForm.tsx    # Dynamic form from stage registry
│       │   ├── StreamingOutput.tsx  # Terminal-style live output
│       │   ├── MarkdownViewer.tsx   # Rendered markdown
│       │   ├── MarkdownEditor.tsx   # Inline editor (CodeMirror) for tweaking output
│       │   ├── ArtifactPicker.tsx   # Select output to pass forward
│       │   └── RunsSidebar.tsx      # Pipeline run list + history
│       ├── hooks/
│       │   ├── useSSE.ts
│       │   └── usePipeline.ts
│       ├── types/
│       │   └── index.ts
│       └── styles/
│           └── main.css
└── workspace/                   # Created at runtime, gitignored
    └── pipelines/
        └── {run_id}/            # Output files per run
```

---

## API Design

### Pipeline Runs
| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/pipelines` | Create a run (name, optional default repo) |
| `GET` | `/api/pipelines` | List all runs |
| `GET` | `/api/pipelines/{id}` | Get run with all executions + artifacts |
| `DELETE` | `/api/pipelines/{id}` | Delete run + workspace |

### Stage Execution
| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/stages/registry` | Stage definitions with skill variants + param schemas |
| `POST` | `/api/stages/execute` | Start a stage (pipeline_run_id, stage, skill, params, input_artifact_id) |
| `GET` | `/api/stages/{execution_id}` | Execution status + metadata |
| `POST` | `/api/stages/{execution_id}/cancel` | Cancel running execution |

### Streaming
| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/stream/{execution_id}` | SSE stream of agent output |

SSE event types:
- `text` — incremental text from the agent
- `tool_use` — agent invoking a tool (tool name + input summary)
- `tool_result` — tool completed
- `thinking` — thinking block (collapsed by default in UI)
- `complete` — execution finished (includes cost_usd, output artifact IDs)
- `error` — execution failed

### Artifacts
| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/artifacts?pipeline_run_id=X` | List artifacts for a run |
| `GET` | `/api/artifacts/{id}/content` | Raw markdown content |
| `PUT` | `/api/artifacts/{id}/content` | Update content (from inline editor) — writes to DB + file on disk |

---

## Stage Registry

Each stage maps to one or more skills with typed parameters:

| Stage | Skills | Key Parameters |
|-------|--------|---------------|
| Scout | `hn-scout`, `hn-scout-generic` | `--top N`, `--repo` |
| Discover | `get-blog-candidates` | `--repo`, `--since`, `--until`, `--limit` |
| Draft | `release-blog`, `write-technical-blog` | `--tag`, `--repo`, topic text |
| Validate | `validate-snippets` | input file (artifact from Draft) |
| Polish | `de-llmify` | input file (artifact from Draft/Validate) |
| Preview | `link-preview` | input file or URL |
| Promote | `write-tweet` | input file, topic, or PR number |

The registry is served by `GET /api/stages/registry` and drives the dynamic `ConfigForm` component.

---

## Agent SDK Integration

### Prompt Construction

```python
# skill_loader.py reads SKILL.md content
# agent_runner.py builds the prompt:

prompt = f"""Follow the instructions below to execute the `{skill_name}` skill.

=== SKILL INSTRUCTIONS ===
{skill_md_content}
=== END SKILL INSTRUCTIONS ===

Execute this skill now with these parameters: /{skill_name} {formatted_params}
"""

# If there's input from a previous stage:
prompt += f"""
The input file from the previous stage is at: {artifact_filename}
(It is already present in the working directory.)
"""
```

### Agent Session

```python
options = ClaudeAgentOptions(
    working_directory=pipeline_workspace_dir,
    permission_mode="acceptEdits",
)
async with ClaudeSDKClient(options=options) as client:
    await client.send_user_message(prompt)
    async for msg in client.receive_response():
        # Push events to SSE queue
```

Each stage execution creates a fresh, isolated agent session.

### Output Detection

After execution completes, `output_manager.py` scans the workspace directory for new/modified files matching expected patterns (`hn-scout-*.md`, `blog-*.md`, `snippet-report-*.md`, etc.) and registers them as artifacts.

Special cases:
- **`get-blog-candidates`** writes no file — the agent's text output is stored as a virtual artifact
- **`de-llmify`** overwrites input in place — backend snapshots the file before execution, stores both versions

---

## Frontend UI

### Layout: Horizontal pipeline + detail panel

```
┌─────────────────────────────────────────────────────────────┐
│  Pipeline: "v0.5.0 release"  ▼                    [+ New]   │
│  [Scout✓] → [Discover✓] → [Draft●] → [Validate] → ...      │
├──────────┬──────────────────────────────────────────────────┤
│ Runs     │  Draft                                           │
│          │  ┌─ Skill ──────────────────────────────────┐    │
│ v0.5.0 ● │  │ ○ release-blog   ● write-technical      │    │
│ HN scan ✓│  └──────────────────────────────────────────┘    │
│          │  ┌─ Config ─────────────────────────────────┐    │
│          │  │ Topic: [PR #676 m-decompose upgrade____] │    │
│          │  │                        [▶ Run Stage]     │    │
│          │  └──────────────────────────────────────────┘    │
│          │  ┌─ Output ─────────────────── [Log|View|Edit]─┐ │
│          │  │ ▸ WebFetch: fetching PR #676...              │ │
│          │  │ Analyzing PR for blog potential...            │ │
│          │  │ # How m-decompose Cut Our Pipeline           │ │
│          │  │ Processing Time by 40%                       │ │
│          │  │ ▸ Write: blog-pr-676-m-decompose.md          │ │
│          │  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ running   │ │
│          │  └──────────────────────────────────────────────┘ │
│          │                        [Pass to Validate →]      │
└──────────┴──────────────────────────────────────────────────┘
```

### Output panel has 3 modes (tab toggle in top-right)

**Log** (default while running): Terminal-style — dark background, monospace, auto-scroll. Tool uses appear as collapsible `▸ ToolName: summary` entries. Progress bar at bottom.

**View** (default after completion): Rendered markdown — `react-markdown` with syntax-highlighted code blocks via `rehype-highlight`. Read-only. This is how you review the output before passing it forward.

**Edit**: Inline markdown editor (CodeMirror with markdown mode). For tweaking a blog draft, fixing a heading, adjusting a sentence before passing to the next stage. Save button writes back to both the DB artifact and the file on disk so subsequent stages pick up the changes.

### Key behaviors
- **PipelineBar**: clickable stages, shows status (pending / running / done / failed)
- **ConfigForm**: generated dynamically from stage registry; includes artifact picker for stages needing input from a prior stage
- **"Pass to Next Stage"**: auto-selects the output artifact as input for the next stage and advances the pipeline bar
- **RunsSidebar**: lists all pipeline runs with their current stage; click to switch between runs

---

## SQLite Schema

```sql
pipeline_runs (id, name, repo_context, created_at)
stage_executions (id, pipeline_run_id, stage, skill_name, status, params_json,
                  input_artifact_id, output_text, cost_usd, started_at, completed_at)
artifacts (id, execution_id, pipeline_run_id, stage, filename, content,
           file_path, created_at)
```

---

## Implementation Order

### Phase 1: Backend skeleton
1. `pyproject.toml` with dependencies (fastapi, uvicorn, claude-agent-sdk, aiosqlite)
2. `config.py` — paths to skills dir, workspace root, DB path
3. `database.py` — SQLite schema creation, connection helper
4. `schemas.py` — Pydantic models
5. `main.py` — FastAPI app with CORS, lifespan (init DB), health endpoint
6. `skill_loader.py` — read SKILL.md files, build stage registry
7. `pipelines.py` router — CRUD for pipeline runs
8. `artifacts.py` router — list/serve/update artifacts

### Phase 2: Agent runner + streaming
9. `agent_runner.py` — prompt construction + SDK integration with event queue
10. `output_manager.py` — file scanning, artifact registration, snapshot logic
11. `stages.py` router — execute stage, get status, cancel
12. `stream.py` router — SSE endpoint consuming the event queue

### Phase 3: Frontend
13. Vite + React + TS scaffolding, Tailwind setup
14. `types/index.ts` — TypeScript types matching backend schemas
15. `api/client.ts` + `api/sse.ts` — fetch wrapper + EventSource wrapper
16. `App.tsx` — layout with sidebar + pipeline bar + main panel
17. `RunsSidebar.tsx` — create/list/select pipeline runs
18. `PipelineBar.tsx` — horizontal stage indicator
19. `StagePanel.tsx` + `ConfigForm.tsx` — skill selector + parameter form + run button
20. `StreamingOutput.tsx` — terminal-style live output (Log tab)
21. `MarkdownViewer.tsx` — rendered output (View tab)
22. `MarkdownEditor.tsx` — CodeMirror editor (Edit tab) + save to `PUT /api/artifacts/{id}/content`
23. `ArtifactPicker.tsx` — select artifacts to pass between stages
24. `useSSE.ts` + `usePipeline.ts` — hooks tying it together

### Phase 4: Integration + polish
25. End-to-end test: run a skill through the full loop
26. Error handling: agent failures, SSE disconnects, missing `gh` CLI
27. Cancel support: interrupt running agent sessions
28. Cost display: show per-execution and cumulative cost

---

## Verification

1. **Start backend**: `cd pipeline-ui && uvicorn backend.main:app --reload`
2. **Start frontend**: `cd pipeline-ui/frontend && npm run dev`
3. **Health check**: `GET /api/health` returns OK + verifies `gh` CLI available
4. **Stage registry**: `GET /api/stages/registry` returns all 7 stages with correct skill variants and params
5. **Run a skill**: Create a pipeline run, execute the Scout stage with `hn-scout-generic --top 5`, verify SSE streams output, artifact is created
6. **Edit an artifact**: Open a completed stage's output, switch to Edit tab, make a change, save — verify the file on disk is updated
7. **Pass between stages**: Run Draft, then Validate with the draft output as input — verify validate-snippets can read the file
8. **Multiple runs**: Start two pipeline runs concurrently, verify they use separate workspace directories and don't interfere
