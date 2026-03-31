---
name: de-llmify
description: >-
  Edit a piece of writing to remove or reduce patterns commonly associated with
  LLM-generated text. Based on research from Kobak et al. 2024, Hacker News,
  and developer community observations about AI writing tells.
---

# De-LLMify a Piece of Writing

Use this skill to edit text so it reads like a human wrote it. The goal is not
to dumb down the writing — it's to remove the mechanical, formulaic patterns
that make readers think "an AI wrote this" and stop trusting the content.

This is especially important for developer relations materials where
credibility is the product.

## Usage

```
/de-llmify [path/to/file.md or inline text]
```

If given a file path, read the file first. If given inline text, work with
that directly.

---

## Step 1: Read and Assess

Read the full text. Before making any changes, score the severity of LLM
tells on a 1–5 scale:

| Score | Meaning | Action |
|-------|---------|--------|
| 1 | Reads human. Minor traces at most. | Light touch — fix only clear tells |
| 2 | Mostly human but a few patterns leak through | Targeted edits |
| 3 | Noticeably LLM-ish to a trained reader | Moderate rewrite of flagged sections |
| 4 | Obviously AI-generated to most developers | Heavy editing pass |
| 5 | "ChatGPT wrote my homework" energy | Consider rewriting from scratch around the core ideas |

Report the score and the top 3 most prominent issues before editing.

---

## Step 2: Word and Phrase Replacement

### Tier 1 — Kill on sight

These words are so strongly associated with LLM output that they pull the
reader out of the text immediately. Replace every instance unless it's
genuinely the best word for the context (rare).

**Words:** delve, tapestry, landscape (used abstractly), realm, multifaceted,
nuanced (as filler), comprehensive (as filler), intricate, pivotal,
commendable, meticulous, noteworthy, groundbreaking, innovative (as filler),
transformative, unparalleled, paramount, foster/fostering, leverage/leveraging,
utilize/utilizing, endeavor, facilitate, underscore, showcase

**Replace with:** plain English. "Use" not "utilize." "Show" not "showcase."
"Important" not "pivotal." "Careful" not "meticulous." If the sentence still
works without the word, delete it entirely.

### Tier 2 — Flag and evaluate

These are overused but sometimes legitimate. Replace when they appear more
than once or when a simpler word works:

bolster, streamline, unveil, illuminate, elucidate, harnessing, synergy,
holistic, robust, dynamic, vibrant, myriad, plethora, cornerstone, paradigm,
juxtapose, interplay, ecosystem (outside biology), moreover, furthermore,
additionally, notably, consequently, inherently, fundamentally, ultimately,
compelling, empower, democratize, reimagine, unlock, elevate, amplify,
curate/curated, seamless/seamlessly, cutting-edge, state-of-the-art, actionable

### Overused phrases — rewrite or delete

| Kill this | Replace with |
|-----------|-------------|
| "In today's [fast-paced/ever-evolving] [world/landscape]..." | Delete. Start with the actual point. |
| "It's important/worth noting that..." | Just state the thing. |
| "Let's dive in" / "Let's delve into" | Delete. |
| "In the realm of..." | "In [topic]" or delete. |
| "A rich tapestry of..." | Delete or use a concrete noun. |
| "Navigate the complexities of..." | "Deal with" or "handle." |
| "This is where X comes in" / "That's where X shines" | State what X does directly. |
| "X is not just Y — it's Z" | Pick the stronger claim and state it once. |
| "Buckle up" | Delete. |
| "Game-changer" | Say what specifically changed. |
| "Everything you need to know about..." | Delete. |
| "The ultimate guide to..." | Delete. |
| "In conclusion" / "To sum up" / "In summary" | Usually delete the whole paragraph. |
| "By doing X, you can Y" | Rewrite to be specific about who and how. |
| "Whether you're a... or a..." | Delete or narrow to the actual audience. |

---

## Step 3: Fix Structural Tells

### Em dash overuse

Count em dashes in the text. A reasonable density is roughly one per 3–4
paragraphs in prose. If there are more:

1. Convert parenthetical em dashes to commas or parentheses
2. Convert em dashes used for elaboration into separate sentences
3. Keep em dashes only where they create genuine emphasis or interruption

**Specifically kill the "It's not X — it's Y" construction.** Rewrite as a
direct statement. "This is a monitoring tool" not "This isn't just a logger
— it's a monitoring tool."

### Bullet point overuse

If the text is more than 40% bullet points by line count, convert some lists
back to prose. Lists are appropriate for:
- Reference material (API parameters, CLI flags)
- Genuinely unordered sets of items
- Step-by-step procedures

Lists are NOT appropriate for:
- Making an argument (use paragraphs)
- Telling a story (use prose)
- Explaining a concept (use sentences that flow into each other)

Watch for the pattern of bolded-keyword-colon lists:
> **Speed**: The new engine is 3x faster.
> **Reliability**: Errors are retried automatically.

This reads like a slide deck. Rewrite as connected prose unless it's truly
reference material.

### Uniform paragraph length

If most paragraphs are 3–5 sentences, vary them. Add some one-sentence
paragraphs. Let some run longer. Human writing has rhythm; LLM writing is
metronomic.

### Over-sectioning

If a 500-word piece has 4+ headers, remove some. Not every idea needs its own
section. Let paragraphs flow into each other with transitions.

### The groups-of-three pattern

LLMs love triplets: "fast, reliable, and scalable." If you see more than one
triplet in a piece, break some up. Use two items. Or four. Or just one.

---

## Step 4: Fix Tone Tells

### Delete sycophantic and cheerleader language

Remove on sight:
- "Great question!"
- "Exciting" / "exciting times"
- "Powerful" (as a generic adjective for any tool)
- "Elegant" (especially about code)
- "Happy coding!"
- "The possibilities are endless!"
- "Let's get started!"
- Any exclamation point that isn't in a direct quote or genuinely surprising
  statement. Most technical prose needs zero exclamation points.

### Replace vague enthusiasm with specifics

| Before | After |
|--------|-------|
| "dramatically faster" | "p99 latency dropped from 3.2s to 800ms" |
| "significantly improved" | "reduced memory usage by 40%" |
| "incredibly powerful" | [delete, or say what it actually does] |
| "blazing fast" | [give the number] |
| "seamlessly integrates with" | "reads from your existing X config" |
| "best-in-class" | [delete, or cite the benchmark] |
| "enterprise-grade" | [delete, or name the specific capability] |

### Reduce hedging

Cut unnecessary qualifiers:
- "It's worth considering that..." → state the thing
- "One could argue that..." → make the argument or don't
- "This could potentially..." → "This can..." or "This does..."
- "In some cases, it might..." → name the cases

But don't remove hedging that reflects genuine uncertainty. "We haven't tested
this on datasets larger than 10GB" is honest, not hedgy.

### Kill the therapist voice

If the text is addressed to a reader and uses phrases like "That's completely
understandable" or "Your feelings are valid" in a technical context, rewrite
to be direct and respectful without being patronizing.

---

## Step 5: Fix Logical and Rhetorical Tells

### Remove question-restating openers

If the text opens by restating the topic as a general statement before getting
to the point, delete the opener:

> ~~"Error handling is a fundamental aspect of software development."~~
> When your API call fails...

### Remove false profundity

Delete or rewrite sentences that attempt to sound deep but say nothing:
- "At its core, programming is about solving problems."
- "In the end, it's not about the technology — it's about the people."
- "The best code is code that doesn't need to exist."

If the insight is real, make it specific. If it's not, delete it.

### Remove both-sides-ism where inappropriate

If the text hedges between two options when the context clearly favors one,
commit to the recommendation. "It depends on your use case" is only acceptable
if the text then describes the specific use cases and what to pick for each.

### Remove circular reasoning

Flag sentences where the "explanation" just restates the claim:
- "X is important because it plays a crucial role" → delete or explain WHY
- "This is useful because it provides utility" → say what it actually enables

### Remove source theater

Vague appeals to authority with no citation:
- "Research has shown..." → cite it or delete
- "Experts recommend..." → name them or delete
- "According to best practices..." → whose practices? Link or delete

---

## Step 6: Increase Information Density

LLM text tends to be puffy — lots of words, not much new information per
sentence. For each paragraph, ask: "What does the reader learn here that
they didn't know from the previous paragraph?"

Specific moves:
- **Delete restating conclusions.** If the final paragraph just summarizes
  what was already said, cut it or replace it with a forward-looking statement.
- **Delete unnecessary introductions.** If the first paragraph is "Context
  you already know" before the actual content starts, cut it.
- **Merge thin paragraphs.** Two paragraphs that make one point should be one
  paragraph.
- **Cut filler transitions.** "Now let's look at..." / "Moving on to..." /
  "With that in mind..." — delete and let the next paragraph speak for itself.

---

## Step 7: Add Human Texture

After removing the LLM patterns, the text may read as clean but flat. If
appropriate for the format (blog posts, tweets — less so for docs), consider
adding:

- **Varied sentence length.** Follow a long sentence with a short one. Or a
  fragment.
- **Concrete specifics** where the original used abstractions. Real numbers,
  real tool names, real error messages.
- **A point of view.** Human writers have opinions. "We chose X over Y
  because..." is more credible than presenting both as equal.
- **Occasional imperfection.** A sentence that starts with "And" or "But."
  A paragraph that's just one sentence. These aren't errors — they're signs
  of a real person writing.

Do NOT overdo this step. The goal is natural writing, not performatively
quirky writing. One or two of these per 500 words is plenty.

---

## Step 8: Write the Edited Version

After editing, write the result:

- If the input was a file, write the edited version to the same file
  (overwrite) unless the user asks otherwise.
- If the input was inline text, output the edited version directly.
- After the edited text, provide a brief changelog listing the categories
  of changes made and how many instances of each were fixed.

### Changelog format

```
## De-LLMify changelog

**LLM-tell score:** [before] → [after]

**Changes:**
- Replaced N Tier 1 words (delve → explore, utilize → use, ...)
- Reduced em dashes from N to N
- Converted N bullet lists to prose
- Removed N filler phrases
- Deleted sycophantic/cheerleader language (N instances)
- Increased information density (deleted N restating paragraphs)
- [any other changes]
```

---

## Step 9: Self-Review Checklist

Before finalizing, verify each item:

| # | Check |
|---|-------|
| 1 | Are all Tier 1 words replaced or justified? |
| 2 | Is em dash density at most ~1 per 3–4 paragraphs? |
| 3 | Is the text less than 40% bullet points by line count? |
| 4 | Are there zero instances of "It's not X — it's Y"? |
| 5 | Are there zero sycophantic openers or cheerleader phrases? |
| 6 | Do vague adjectives ("powerful," "elegant") have specifics or deletion? |
| 7 | Does the opening get to the point without restating the topic? |
| 8 | Is there no "In conclusion" summary that just repeats what was said? |
| 9 | Are paragraphs varied in length (not all 3–5 sentences)? |
| 10 | Does the text have a point of view, not just both-sides-ism? |
| 11 | Would a skeptical developer on Hacker News read this without rolling their eyes? |
| 12 | Did the edit preserve the original meaning and technical accuracy? |

---

## Common Mistakes to Avoid

- **Over-correcting into bland prose**: the goal is natural writing, not
  stripping all style. Keep strong verbs, vivid examples, and real voice.
- **Breaking technical accuracy to sound casual**: never sacrifice correctness
  for tone. "About 3x faster" is fine if the real number is 2.8x–3.2x. Just
  don't round 1.4x to "much faster."
- **Replacing every em dash**: some em dashes are the right choice. The
  problem is density, not existence.
- **Adding forced personality**: sprinkling in "honestly" and "look," or
  starting every other sentence with "But" is just trading one set of tells
  for another.
- **Ignoring context**: documentation has different norms than blog posts.
  A reference page with lots of bullet points and headers is fine. A blog
  post that reads like a reference page is not.
- **Missing new tells while fixing old ones**: if you rewrite a sentence and
  the rewrite uses a Tier 1 word, catch it.

---

## Related Skills

- `/write-technical-blog` — apply de-LLMify as a final editing pass after
  drafting a blog post
- `/write-tweet` — tweets are short enough that even one LLM tell stands out;
  run this on drafted tweet threads
