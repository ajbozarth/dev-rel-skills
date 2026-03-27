# Mellea v0.4.0: Plugins, Observability, and Expanded Intrinsics

Every generative application eventually needs the same three things: a way to observe what models are doing, a way to intercept and extend behavior without forking the library, and a richer vocabulary of built-in capabilities. Before v0.4.0, getting all three meant writing your own wrappers, patching internals, or reaching for a separate framework entirely.

Mellea v0.4.0, released March 18, 2026, addresses all three in one release. The headline addition is a fully-featured plugin and hook system. Alongside it, OpenTelemetry observability reaches a mature state with token usage tracking, configurable metrics exporters (OTLP and Prometheus), and a dedicated logging export path. And the intrinsics library adds four new safety and attribution capabilities backed by IBM Granite.

---

## A Hook System for Every Stage of the Pipeline

Until now, extending Mellea required either subclassing core types or monkey-patching call sites — neither approach survives an upgrade.

[#582](https://github.com/generative-computing/mellea/pull/582) introduces `mellea.plugins`: a first-class hook system that lets you register handlers at defined points across the session, generation, sampling, component, tool, and validation pipelines. It builds on the [cpex](https://github.com/contextforge-org/contextforge-plugins-framework) framework, installed as an optional `hooks` extra.

Your first plugin in under 30 lines:

```python
from mellea import start_session
from mellea.plugins import HookType, hook, register

@hook(HookType.GENERATION_PRE_CALL)
async def log_generation(payload, ctx):
    """Log a one-line summary before every LLM call."""
    action_preview = str(payload.action)[:80].replace("\n", " ")
    print(f"[generation] About to call LLM: {action_preview!r}")

register(log_generation)

with start_session() as m:
    result = m.instruct("What is the capital of France?")
```

Hooks support four execution modes — `SEQUENTIAL`, `CONCURRENT`, `AUDIT`, and `FIRE_AND_FORGET` — and a `priority` parameter controls ordering when multiple plugins share the same hook point. Plugins can block execution by setting `block=True` in their result; the runtime raises a `PluginViolationError` and halts the call.

The full hook surface covers 20 payload types across six categories: session lifecycle, generation pre/post call, sampling loop (start, iteration, repair, end), component pre/post execute, tool pre/post invoke, and validation pre/post check. A write-protection policy per hook type prevents plugins from mutating fields they shouldn't touch.

The plugin system is opt-in: all plugin paths guard with `try/except ImportError`, and every stdlib call site is a no-op when `cpex` is not installed. See the [six quickstart examples](https://github.com/generative-computing/mellea/tree/main/docs/examples/plugins) for standalone hooks, class-based plugins, session-scoped plugins, plugin sets, concurrent hooks, and tool hooks.

---

## Full OpenTelemetry Observability: Tokens, Metrics, and Logs

Three separate PRs complete Mellea's OpenTelemetry story in this release.

**Token usage metrics** ([#563](https://github.com/generative-computing/mellea/pull/563)) adds `mellea.llm.tokens.input` and `mellea.llm.tokens.output` counters tracked across all five backends — OpenAI, Ollama, WatsonX, LiteLLM, and HuggingFace. Every metric carries Gen-AI semantic convention attributes (`gen_ai.system`, `gen_ai.request.model`, `mellea.backend`) so dashboards built on the OTel spec work without glue code.

**Configurable metrics exporters** ([#610](https://github.com/generative-computing/mellea/pull/610)) lets you route those metrics to where you actually run your observability stack:

```bash
# Console (debug)
export MELLEA_METRICS_ENABLED=true
export MELLEA_METRICS_CONSOLE=true

# OTLP (production)
export MELLEA_METRICS_ENABLED=true
export MELLEA_METRICS_OTLP=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Prometheus scrape endpoint on :9464/metrics
export MELLEA_METRICS_ENABLED=true
export MELLEA_METRICS_PROMETHEUS=true
```

Multiple exporters can be enabled simultaneously.

**OTLP logging export** ([#635](https://github.com/generative-computing/mellea/pull/635)) brings the same configurability to structured logs, rounding out the tracing + metrics + logging triad. The telemetry docs were refactored into dedicated pages for each signal type ([#662](https://github.com/generative-computing/mellea/pull/662)) — see the [tracing](https://github.com/generative-computing/mellea/blob/main/docs/docs/evaluation-and-observability/tracing.md), [metrics](https://github.com/generative-computing/mellea/blob/main/docs/docs/evaluation-and-observability/metrics.md), and [logging](https://github.com/generative-computing/mellea/blob/main/docs/docs/evaluation-and-observability/logging.md) pages.

---

## Four New Safety and Attribution Intrinsics

Mellea's intrinsics library now includes four new capabilities from the `ibm-granite/granitelib-guardian-r1.0` and `ibm-granite/granitelib-core-r1.0` model family.

**Guardianlib intrinsics** ([#678](https://github.com/generative-computing/mellea/pull/678)) adds:

- `policy_guardrails()` — checks whether a scenario complies with a given policy (Yes / No / Ambiguous)
- `guardian_core()` — safety risk detection via the `<guardian>` protocol tag, covering harm, social bias, jailbreak, profanity, violence, groundedness, answer relevance, context relevance, and function call hallucination through a built-in `CRITERIA_BANK`
- `factuality_detection()` and `factuality_correction()` — detect and correct factually incorrect responses relative to a provided context

**Context attribution** ([#679](https://github.com/generative-computing/mellea/pull/679)) adds `find_context_attributions()`, which identifies which sentences in prior conversation messages and RAG documents were most important to the model when generating each response sentence. It follows the same pattern as the existing `find_citations()` function.

**UQ and requirement_check as core intrinsics** ([#551](https://github.com/generative-computing/mellea/pull/551)) promotes uncertainty quantification and requirement checking into the `core` intrinsic namespace, making them available without importing the full RAG toolkit. Example usage is in [`docs/examples/intrinsics/`](https://github.com/generative-computing/mellea/tree/main/docs/examples/intrinsics).

---

## Granite-Common Merged into Mellea

[#571](https://github.com/generative-computing/mellea/pull/571) moves the functionality that previously lived in the `granite-common` library directly into `mellea`. This eliminates a separate dependency for users of Granite-backed intrinsics and adapter features, and consolidates the CODEOWNERS structure.

---

## Other Improvements

**Intrinsics fixes:**
- **Removed `answer_relevance*` intrinsics**: The answer relevance intrinsics were removed along with several other intrinsic-layer fixes. ([#690](https://github.com/generative-computing/mellea/pull/690))
- **DropDuplicates key bug**: Fixed a generator-vs-tuple bug that caused incorrect deduplication behavior in `DropDuplicates`. ([#652](https://github.com/generative-computing/mellea/pull/652))

**Repair loop improvement:**
- **Validation failure reasons in repair messages**: `MultiTurnStrategy` now includes the failure reason in repair prompts, giving the model better context when retrying. ([#633](https://github.com/generative-computing/mellea/pull/633))

**Streaming fix:**
- **`ModelOutputThunk.astream` exception safety**: Fixed a bug where `post_process` was called before `finally` in `astream`, causing incorrect behavior on exceptions. ([#580](https://github.com/generative-computing/mellea/pull/580))

**Backend fixes:**
- **HuggingFace `mot.usage` always populated**: Token usage was not always set on HuggingFace responses. ([#697](https://github.com/generative-computing/mellea/pull/697))
- **HuggingFace device_map**: Fixed model loading to use `device_map` correctly. ([#587](https://github.com/generative-computing/mellea/pull/587))
- **Optional import guard for hooks**: Plugin imports are now safely guarded when `cpex` is not installed. ([#627](https://github.com/generative-computing/mellea/pull/627))

**New example:**
- **Qiskit code validation IVR**: A full instruct-validate-repair example that generates and validates Qiskit quantum circuits. ([#576](https://github.com/generative-computing/mellea/pull/576))

**Documentation:**
- Complete developer documentation rewrite ([#601](https://github.com/generative-computing/mellea/pull/601)) and API pipeline overhaul ([#611](https://github.com/generative-computing/mellea/pull/611)) — the docs site is substantially improved in this release.
- Plugins page added to nav with standards applied ([#663](https://github.com/generative-computing/mellea/pull/663)).
- Examples catalogue updated with missing categories ([#672](https://github.com/generative-computing/mellea/pull/672)).

---

## Upgrading

```bash
pip install --upgrade mellea
```

The plugin system requires the optional `hooks` extra:

```bash
pip install --upgrade "mellea[hooks]"
```

See the [full release notes](https://github.com/generative-computing/mellea/releases/tag/v0.4.0) for the complete changelog.

---

<!--
Drafted from: generative-computing/mellea v0.4.0 (https://github.com/generative-computing/mellea/releases/tag/v0.4.0)
Highlight PRs: #582, #679, #678, #610, #563, #551, #571, #553, #635, #690, #672, #633, #576  (score ≥ 50)
Mention PRs:   #669, #570, #686, #665, #663, #662, #611, #601, #596, #594, #569, #658, #605, #685, #627, #614, #602, #580, #555, #619  (score 10–49)
Skipped PRs:   #697, #652, #646, #637, #623, #595, #587, #579, #670, #664  (score < 10)
-->
