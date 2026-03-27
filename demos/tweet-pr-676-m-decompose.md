# Tweet: m-decompose pipeline upgrade

> Source: https://github.com/generative-computing/mellea/pull/676
> Date: 2026-03-26

---

## Primary thread

**Tweet 1** (~271 chars)
Give an LLM a complex task and it either hallucinates constraints or ignores them entirely.

`m decompose` now extracts, validates, and generates runnable checks for every constraint in your task — before a single line of code runs.

Thread:

---

**Tweet 2** (~198 chars)
The old pipeline guessed at constraints from task descriptions.

Order-sensitive. Layout-sensitive. Subtask IDs shifted if you rewrote a sentence.

Downstream templates broke silently. You wouldn't know until the final output was wrong.

---

**Tweet 3** (~246 chars)
The new pipeline has four explicit stages:

1. Extract constraints (normalize → parse, stable IDs)
2. Decide validation strategy per constraint (LLM or code)
3. Generate a validation module — callable functions, not descriptions
4. Execute subtasks in dependency order

Each stage is decoupled and reusable.

---

**Tweet 4** (~207 chars) ⭐ most shareable
Before: a JSON blob describing what *should* be validated
After: a Python module you can import and call

```python
from output.validations import check_daily_distance, check_sunset_count
check_daily_distance(itinerary)  # raises if violated
```

The output is now runnable, not just readable.

---

**Tweet 5** (~189 chars)
Net: deleted 3,500 lines, added 1,800. The pipeline is smaller and does more.

Honest caveat: constraint extraction still depends on the LLM following structure. Noisy task descriptions can produce noisy constraints — garbage in, garbage out.

---

**Tweet 6** (~155 chars)
Try it:
```bash
m decompose run --input-file task.txt --out-dir ./output/
```

Examples: github.com/generative-computing/mellea/tree/main/docs/examples/m_decompose

---

**Media:** Screenshot of before (raw JSON constraint description) next to after (generated Python validation function). Use Ray.so for the code panel. Tweet 4 is the one people will screenshot and share — make sure the before/after contrast is visually obvious.

**Timing:** Post Tue-Thu, 9-11am ET. Don't compress to a single tweet — the validation-as-runnable-module insight needs tweet 4 to land.

---

## Alternative opener

Deleted 3,500 lines from `m decompose` this week. Added 1,800. The pipeline is smaller, has more capability, and the output is now a Python module you can actually run. (~172 chars)

> Use this if you want a number-led single tweet instead of a thread.
