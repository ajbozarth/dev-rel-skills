# M-Decompose: Turn Any Complex Task Into a Runnable LLM Pipeline

When a task is too long or too structured for a single prompt, most developers resort to one of two bad options: either split it manually and wire the pieces together by hand, or pile everything into one massive prompt and hope the model tracks the constraints. Both approaches break at the seams as tasks grow.

`m decompose` solves this by doing the splitting for you — automatically, in a form you can immediately run.

## The problem: complex prompts are fragile

Consider a realistic task: plan a 3-day trip to the Grand Canyon with daily mileage caps, required sunrise viewpoints, and a specific set of constraints about timing. Writing this as a single prompt puts all the pressure on one LLM call to track every constraint, maintain internal consistency, and produce structured output across a dozen distinct deliverables.

Before this upgrade, mellea's decompose pipeline had this shape but lacked precision. Constraint extraction was layout-sensitive — reordering bullets or adding whitespace could silently change which constraints were identified, producing different subtask bindings on each run.

## What's new: a deterministic, inspectable pipeline

The upgraded `m decompose` pipeline has five explicit stages, each with a clean interface:

```
Task Prompt
     ↓
1. Subtask listing      — ordered list of what needs to happen
     ↓
2. Constraint extraction — what the output must satisfy (normalized)
     ↓
3. Validation decision  — per-constraint strategy: "llm" or "code"
     ↓
4. Prompt generation    — Jinja2 template per subtask, with {{ deps }}
     ↓
5. Constraint assignment — bind constraints to the subtasks that own them
```

Each stage is independently addressable. The key improvement is in stages 2 and 3.

### Stable constraint extraction

Previously, constraint extraction depended on raw text layout. Now the input goes through whitespace canonicalization, separator unification, and newline-aware block segmentation before parsing. The result: the same logical constraints produce the same constraint IDs regardless of how the original prompt was formatted.

This matters downstream. Subtasks reference constraints by ID. Unstable IDs meant template reproducibility was fragile — running decompose twice on the same prompt could produce prompts with different variable names.

### Validation as a first-class decision

This release promotes validation strategy from an implicit implementation detail to an explicit, inspectable field in the output. Each constraint now carries a `val_strategy`:

```python
{
  "constraint": "Total budget must not exceed $400",
  "val_strategy": "code",   # ← generate a runnable validation function
  "val_fn": "def validate_budget(items): ...",
  "val_fn_name": "validate_budget"
}
```

Constraints that can be checked programmatically (numeric bounds, counts, required fields) get `"code"` — the pipeline generates a runnable Python stub. Constraints that require reasoning ("the tone should be appropriate for children") get `"llm"`.

The validation code generator uses in-context learning examples to produce consistent, callable function stubs:

```python
from mellea.cli.decompose.pipeline import decompose, DecompBackend

result = decompose(
    task_prompt="""
    Plan a 3-day Grand Canyon itinerary for early May.
    Daily walking distance must stay under 6 miles.
    Each day must include at least one sunrise or sunset viewpoint.
    """,
    model_id="granite4:micro",
    backend=DecompBackend.ollama,
)

# Inspect extracted constraints and their validation strategies
for c in result["identified_constraints"]:
    print(f"{c['val_strategy']:5} | {c['constraint']}")
```

Output:

```
code  | Daily walking distance must stay under 6 miles
llm   | Each day must include at least one sunrise or sunset viewpoint
```

## Before and after: what the output looks like

The V1 output was a structured decomposition result — a JSON blob describing the plan. The V2 output is an **importable, runnable validation module** alongside the plan:

**Before (V1):**

```python
# m_decomp_result_v1.py — description only
# Subtask 1: Create itinerary ...
# Constraints: walking distance < 6 miles
# No runnable validation
```

**After (V2):**

```python
# m_decomp_result_v2.py — generated, importable
def validate_daily_distance(itinerary_day: dict) -> bool:
    """Returns True if the day's walking distance is under 6 miles."""
    total_miles = sum(leg.get("miles", 0) for leg in itinerary_day.get("legs", []))
    return total_miles < 6

VALIDATION_MAP = {
    "daily_distance": validate_daily_distance,
    # llm-validated constraints are referenced by name for a separate check pass
}
```

Downstream code no longer needs to re-interpret constraint descriptions. It calls the function directly.

## Running it

Via CLI:

```bash
# Write your task to a file
cat > task.txt << 'EOF'
I will visit Grand Canyon National Park for 3 days in early May.
Daily walking distance must stay under 6 miles.
Each day must include at least one sunrise or sunset viewpoint.
EOF

# Run decompose
mkdir -p ./output
m decompose run --input-file task.txt --out-dir ./output/ --log-mode demo

# Execute the generated plan
python output/m_decomp_result.py
```

Via Python API:

```python
from mellea.cli.decompose.pipeline import decompose, DecompBackend
import json

result = decompose(
    task_prompt=open("task.txt").read(),
    model_id="mistralai/Mistral-Small-3.2-24B-Instruct-2506",
    backend=DecompBackend.openai,
    backend_endpoint="http://localhost:8000/v1",
    backend_api_key="EMPTY",
)

print(json.dumps(result, indent=2, ensure_ascii=False))
```

The `log_mode` argument separates debug output (full prompt/response traces) from the demo view (stage-by-stage progress). Pass `--log-mode debug` to inspect what each stage sent and received.

## Limitations worth knowing

- **Model quality matters.** Small models (< 7B parameters) produce inconsistent subtask tags, which breaks template variable binding. `granite4:micro` works for simple tasks; use a 24B+ model for multi-step plans with many constraints.
- **Code-validated stubs are not tested.** The generated `val_fn` stubs are syntactically valid Python but are not unit-tested. Treat them as starting points for your own validation logic, not production-ready checks.
- **Single-task prompts don't benefit.** If your prompt fits comfortably in one call, use `m.instruct()` directly. Decomposition adds latency and LLM calls.

## Try it

If you've been hitting the limits of single-prompt generation — inconsistent constraint enforcement, outputs that drift across retries, validation logic you have to rebuild by hand — `m decompose` now gives you a structured, reproducible alternative.

```bash
uv add mellea
m decompose run --input-file task.txt --out-dir ./output/
```

Full working examples are in [`docs/examples/m_decompose/`](https://github.com/generative-computing/mellea/tree/main/docs/examples/m_decompose). Reference docs are at the [m decompose guide](https://github.com/generative-computing/mellea/blob/main/docs/docs/guide/m-decompose.md).

---

> **Before publishing:** Verify the `--log-mode demo` CLI flag name against the actual
> `decompose run --help` output, and confirm the V2 Jinja2 template structure in
> `cli/decompose/m_decomp_result_v2.py.jinja2` matches the "After" snippet above.
