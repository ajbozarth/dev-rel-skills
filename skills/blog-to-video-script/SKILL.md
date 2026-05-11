---
name: blog-to-video-script
description: >-
  Convert a technical blog post, article, or piece of writing into a shootable
  video script with on-screen cues, timing estimates, and delivery notes. Use
  this skill whenever the user wants to turn a blog, post, article, README,
  release note, or any long-form writing into a script for a short-form video,
  a screen-recording demo, or a conference-style talk — even if they don't say
  the word "script" (e.g. "make this into a YouTube video", "can we film this",
  "adapt this for TikTok", "turn this into a talk"). Pairs naturally after
  /write-technical-blog and before /de-llmify.
---

# Blog → Video Script

Turn a written piece into a script someone can actually shoot. The output is
not the blog read aloud — it is a re-authored piece of writing designed for
ear, eye, and camera.

## Usage

```
/blog-to-video-script [input] [--mode short|demo|talk]
```

- `[input]` — one of:
  - a local file path (e.g. `blog-foo.md` or `./drafts/post.md`)
  - a URL (e.g. `https://example.com/post`)
  - raw pasted text (any other shape)
- `--mode` — optional. If omitted, default to `demo` and say so in the
  output.

### How to resolve the input

Inspect the arg shape, in this order:

1. **Starts with `http://` or `https://`** → fetch with WebFetch. Ask it for
   the full article text, headings preserved.
2. **Ends with `.md`, `.txt`, or `.mdx`, OR exists on disk** → read with
   Read.
3. **Otherwise** → treat the full arg string as the raw source text.

If the arg is empty, ask the user what to adapt.

### How to resolve the mode

If the user did not specify `--mode`, default to `demo` but briefly state
which mode you picked and what the alternatives are, so they can redirect
in one turn. Example: "Drafting in `demo` mode (3–5 min screen-recording
walkthrough). Ask for `--mode short` (60–90s) or `--mode talk` (10–15
min) if you'd rather."

---

## The Three Modes

The mode determines target length, pacing, and production style. Pick
section durations so they sum to the target length.

| Mode | Target length | Feel | Spine |
|------|---------------|------|-------|
| `short` | 60–90 seconds | TikTok / Shorts / Reels. Single speaker, fast, punchy. | Hook → 2–3 beats → CTA. |
| `demo` | 3–5 minutes | YouTube dev-content screen recording. Narration supports what's on screen. | **On-screen action is the spine**; narration serves it. |
| `talk` | 10–15 minutes | Conference-style narrative with slides. | Story arc across 4–6 sections with clear transitions. |

---

## What a Video Script Is (and Isn't)

A video script is not the blog with line breaks. The ear and the page have
different appetites. Before drafting, internalize these shifts:

- **Cut 60–80% of the prose.** Most blog paragraphs become one or two
  spoken sentences. Any sentence that doesn't earn its airtime is cut.
- **Lead with the payoff.** The hook is the result, the demo, or the
  surprising claim — not the background. Background is earned after the
  viewer has a reason to care.
- **Short sentences. One idea per breath.** Long nested clauses that read
  fine on the page sound like molasses spoken aloud.
- **Repeat the thesis.** Viewers drift. A key idea said once is a key idea
  missed. State it in the hook, echo it mid-way, land it at the end — in
  different words each time.
- **Narrate code in plain language.** Don't read syntax character by
  character. "We ask the API for the user, passing the token" beats
  reciting `client.users.get(token=token)`.
- **Every section needs a reason to keep watching.** End sections on a
  question, a tension, or a tease. "But there's a catch." "Here's where it
  got weird." "Watch what happens when we run this."
- **Write for performance, not for reading.** If you wouldn't say it out
  loud, don't write it. Read it back in your head at speaking pace.

For `demo` mode specifically: start from **what the viewer is looking at**,
not from what the narrator is saying. Block the on-screen actions first,
then write narration that fits underneath them. If the narration is doing
all the work and the screen is static, cut to B-roll or restructure.

---

## Production Cues (required in every output)

The script must be directly shootable. Weave these cues inline, formatted
as bracketed tags so they visually separate from narration:

- **Visual / on-screen cues**
  - `[SHOW: terminal running npm test, tests pass in green]`
  - `[CODE: app/api/route.ts lines 12–28, highlight the new middleware]`
  - `[B-ROLL: architecture diagram, left-to-right data flow]`
  - `[SCREEN: browser at localhost:3000, click the "New" button]`
  - `[CUT TO: speaker on camera]`
  - `[SLIDE: "Three problems with the old approach"]` (talk mode)

- **Timing estimates** — put a duration target at the start of every
  section, in the form `(0:00–0:15, ~15s)`. Durations should sum to the
  target length for the chosen mode. At the very top of the script, show a
  one-line budget: `Target: 4:00 total`.

- **Delivery notes** — inline parentheticals that guide the speaker's
  tone:
  - `(pause)` — a beat of silence for emphasis
  - `(emphasis)` — lean on this word
  - `(casual)` — conversational, low stakes
  - `(slow down)` — for a technical term the viewer needs to absorb
  - `(excited)` — genuine energy, not hype
  - `(drop in pitch)` — the "landing" at the end of a thought

Use cues liberally enough that someone else could shoot this, sparingly
enough that narration still reads as prose.

---

## Output Structure

Use this skeleton. Adapt section count to the mode — `short` collapses the
middle, `talk` expands it.

```markdown
# Video Script: <Title>

**Mode:** <short | demo | talk>
**Target length:** <e.g. 4:00>
**Source:** <path/url, or "pasted text">
**One-line thesis:** <the single sentence the viewer should leave with>

---

## Cold Open / Hook  (0:00–0:15, ~15s)

[SHOW: …]
Narration with (delivery notes) inline.

## Section 1 — <name>  (0:15–1:00, ~45s)

[SHOW / CODE / B-ROLL: …]
Narration.

## Section 2 — <name>  (1:00–2:30, ~1:30)

…

## Payoff / Demo  (2:30–3:30, ~1:00)

[SHOW: the working thing]
…

## CTA  (3:30–4:00, ~30s)

[CUT TO: speaker on camera]
"If you want to try this yourself, <one specific action>. Link below."

---

## Shot list (appendix)

- 0:00 — terminal, dark theme, `npm test` ready to run
- 0:15 — editor split, file X open
- …

## Notes for the editor

- Suggested music: low-energy under narration, kick at the reveal
- Suggested captions: all narration, burn-in for code file paths
- Watch for: dead air longer than 2s; re-record any stumble over <term>
```

The **shot list** and **editor notes** are short and optional for `short`
mode, expected for `demo` and `talk`.

### Mode-specific scaffolds

**`short` (60–90s):**

```
Hook (0:00–0:05, ~5s)
Beat 1 (0:05–0:25)
Beat 2 (0:25–0:50)
Beat 3 / payoff (0:50–1:15)
CTA (1:15–1:30)
```

**`demo` (3–5 min):** the default scaffold above.

**`talk` (10–15 min):**

```
Cold open / story (0:00–1:00)
Thesis slide (1:00–1:30)
Problem section (1:30–4:00)
Approach / walkthrough (4:00–9:00)
Demo or result (9:00–11:30)
Trade-offs + what's next (11:30–13:30)
Close + CTA (13:30–14:30)
```

For `talk` mode, include `[SLIDE: ...]` cues alongside narration. The
speaker notes underneath each slide heading should be what the speaker
actually says, not bullet-pointed reminders.

---

## Drafting Process

1. **Read the source end to end** before writing anything. Identify:
   - the single most surprising claim, result, or demo
   - the one-sentence thesis
   - the strongest before/after, metric, or visual
   - the CTA (link, repo, docs) — every script needs exactly one
2. **Pick the hook.** The hook is almost never the blog's opening
   paragraph. It's usually buried near the demo or the payoff. Steal from
   there.
3. **Outline section-by-section with timings** before writing any
   narration. Confirm the durations sum to the target.
4. **Block visuals first for `demo` mode.** Write the `[SHOW: ...]` list
   top to bottom, then write narration that fits under it.
5. **Draft narration in short sentences.** Read it back at speaking pace.
   If a sentence runs past ~15 words, break it.
6. **Add delivery notes last.** Over-annotating early makes the script
   feel stage-managed; add them where a read-through reveals a pacing or
   emphasis risk.
7. **Write to file** (see below).

---

## Write to File

Save the script to the current working directory:

- **Filename:** `video-script-<slug>-<mode>.md`
  - `<slug>` is a short kebab-case summary of the topic (reuse the source
    filename's slug if the input was a local `.md`)
  - `<mode>` is `short`, `demo`, or `talk`
  - Examples: `video-script-rate-limiting-demo.md`,
    `video-script-pr-676-m-decompose-talk.md`
- Use the Write tool. Do not ask — just write it.
- After writing, tell the user the filename and suggest obvious next
  steps: "Run `/de-llmify video-script-<slug>-<mode>.md` to tighten the
  prose before recording."

---

## Self-Review Checklist

Before handing off, verify:

| # | Check |
|---|-------|
| 1 | Does the hook state the payoff, not the background? |
| 2 | Is the thesis stated at least twice, in different words? |
| 3 | Do section durations sum to the target length? |
| 4 | Does every section have at least one visual cue? |
| 5 | For `demo` mode: is the on-screen action the spine, with narration serving it? |
| 6 | Are sentences short enough to say in one breath? |
| 7 | Is code narrated in plain language, not read character-by-character? |
| 8 | Does each section end with a reason to keep watching? |
| 9 | Is there exactly one CTA, and is it a specific action (not "check it out")? |
| 10 | Did you cut 60–80% of the source prose, or is the script still bloated? |
| 11 | Are delivery notes `(pause)` / `(emphasis)` present where the read needs them? |
| 12 | Could a second person shoot this from the script alone, without asking you questions? |

---

## Common Mistakes to Avoid

- **Reading the blog aloud.** If a sentence appears verbatim from the
  source, it probably shouldn't. Spoken prose is different prose.
- **No visuals for minutes at a time.** Even a talking-head section should
  cut to a slide, a diagram, or a code snippet every 15–30 seconds.
- **Over-scripting the speaker.** Delivery notes on every sentence kills
  natural read. Use them where they matter.
- **Burying the demo.** In `demo` mode, the working thing should appear on
  screen within the first 20 seconds, even as a teaser.
- **Multiple CTAs.** Pick one. "Star the repo AND try the demo AND join
  Discord" is zero CTAs.
- **Durations that don't add up.** If the section budgets sum to 7 minutes
  for a "5-minute demo," the pacing is already broken on paper. Fix it
  before drafting narration.
- **Code recited character-by-character.** Nobody wants to hear
  "client dot users dot get open paren token equals token close paren."
  Say what the code *does*.
