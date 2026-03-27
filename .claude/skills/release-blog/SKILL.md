---
name: release-blog
description: >-
  Fetch the latest GitHub release for generative-computing/mellea, score and
  rank its PRs by blog-worthiness, then draft a narrative release blog post
  highlighting the most impactful changes.
---

# Draft a Release Blog Post from the Latest GitHub Release

Fetch the latest release from `generative-computing/mellea`, identify the
highest-impact changes, and produce a publication-ready blog post draft.

## Usage

```
/release-blog [--tag vX.Y.Z] [--repo owner/repo]
```

Defaults: `--tag` = latest release, `--repo` = `generative-computing/mellea`.

---

## Step 1: Fetch the Release

Get the release body and metadata:

```bash
# If no tag specified, fetch the latest
gh release view --repo generative-computing/mellea \
  --json tagName,name,publishedAt,body,url
```

If `--tag` was provided, use:

```bash
gh release view vX.Y.Z --repo generative-computing/mellea \
  --json tagName,name,publishedAt,body,url
```

Record: `tagName`, `publishedAt` (format as `Month DD, YYYY`), `body`, `url`.

---

## Step 2: Extract PR Numbers from the Release Body

Parse the release `body` for PR references. They appear as `(#1234)` or
`#1234` in lines like:

```
* feat: add streaming support (#1042) by @author
```

Extract every PR number mentioned. Deduplicate. You should typically find
5–30 PRs in a release.

---

## Step 3: Fetch PR Metadata

For each extracted PR number, fetch:

```bash
gh pr view PR_NUMBER --repo generative-computing/mellea \
  --json number,title,body,labels,additions,deletions,files,author,mergedAt
```

Collect: `title`, `labels[].name`, `additions + deletions` (net lines),
`files[].path` (file paths changed), `author.login`.

---

## Step 4: Score Each PR for Blog Prominence

Apply the scoring rubric below. Higher score = more space in the blog post.

| Signal | Points |
|--------|--------|
| Title starts with `feat:` or `feat(` | **+40** |
| Label `enhancement` or `feature` | **+20** |
| Any changed file under `docs/examples/` | **+25** |
| Any changed file under `docs/docs/` | **+15** |
| Any changed `.md` file anywhere | **+10** |
| Net lines changed ≥ 500 | **+15** |
| Net lines changed ≥ 200 | **+10** |
| Net lines changed ≥ 50 | **+5** |
| Label `breaking-change` | **+30** (must be prominently featured) |
| Title starts with `fix:` | **+5** |
| Title starts with `chore:`, `ci:`, `build:` | **−30** (infra noise) |
| Author is `dependabot[bot]` or `renovate[bot]` | **−40** (dep bumps) |

Sort PRs descending by score. Assign tiers:

- **Highlight** (score ≥ 50): Gets its own H2 section with narrative
- **Mention** (score 10–49): Grouped bullet in a summary section
- **Skip** (score < 10): Omit from the post entirely

---

## Step 5: Identify the Release Theme

Look at the **Highlight** PRs and ask: what is the single unifying story?

Examples:
- "This release focuses on making streaming first-class"
- "v0.5.0 lays the foundation for multi-agent workflows"
- "A performance release: 3 independent improvements that cut latency"

If there's no clear theme, lead with the single highest-scoring PR.

The theme becomes the **opening hook** of the blog post.

---

## Step 6: Draft the Blog Post

Use the following structure. The post should read like an engineer wrote it,
not a changelog or press release.

### Title

Follow the pattern from `/write-technical-blog`:
- Lead with the **outcome or problem solved**, not the version number.
- Include the project name and version for SEO.
- Target 50–60 characters.
- Patterns: `[Feature]: what it enables in Mellea vX.Y.Z` or
  `How [theme] works in Mellea vX.Y.Z`

### Opening Hook (2–3 paragraphs)

- State the problem the reader already has (the "before" world).
- Name the release and date: "Mellea vX.Y.Z, released [date],"
- State what changes: one sentence on the release theme.
- Include one concrete metric if available ("reduces boilerplate from 40
  lines to 8", "3× faster on sequential chains").

### Breaking Changes (if any)

If any PR has label `breaking-change` or title contains `breaking`, add
this section **immediately after the opening**, before any features:

```markdown
## ⚠️ Breaking Changes

- **What changed**: one sentence.
- **Who is affected**: users who...
- **Migration**: step-by-step or link to migration guide.
```

Never bury breaking changes later in the post.

### Feature Highlights (one H2 per Highlight-tier PR)

For each Highlight PR, in descending score order:

```markdown
## [What the feature enables, not its internal name]

[1 paragraph: the problem before this PR. Show old code if instructive.]

[1–2 paragraphs: what changed and how to use it. Show new code.]

[1 sentence: what this unlocks for the reader.]
```

Rules for this section:
- Every code block must have a language specifier (` ```python `, ` ```bash `).
- Use before/after snippets when the API changed.
- Do not invent code. If you don't have example code, say "see the [docs
  link] for a full example."
- If the PR touched `docs/examples/`, link to the example file on GitHub.

### Other Improvements

For Mention-tier PRs, group into a single section with a short bullet per
PR:

```markdown
## Other Improvements

- **[Short label]**: [one sentence describing the user-visible change].
  ([#1234](url))
- **[Short label]**: ...
```

Group related fixes together (e.g., "Backend fixes", "CLI improvements") if
5+ fall into a natural cluster.

### Upgrade

```markdown
## Upgrading

```bash
pip install --upgrade mellea
```

See the [full release notes](RELEASE_URL) for the complete changelog.
```

If there were breaking changes, repeat the migration pointer here.

---

## Step 7: Self-Review Before Outputting

Check each item before producing the final post:

| # | Check |
|---|-------|
| 1 | Does the **opening state a problem**, not the solution? |
| 2 | Are **breaking changes first** (before features)? |
| 3 | Does each Highlight section have a **before/after** or working code snippet? |
| 4 | Are all code blocks **fenced with language specified**? |
| 5 | Does every PR mention include its **#number and link**? |
| 6 | Is there exactly **one primary CTA** (the release URL or upgrade command)? |
| 7 | Are dep-bump and infra PRs **absent** from the post? |
| 8 | Does the title name an **outcome or problem**, not just "vX.Y.Z released"? |
| 9 | Does the post read like **one coherent story**, not a list of unrelated items? |
| 10 | Are **no examples invented** — only code from the PRs or docs? |

---

## Output Format

Write the blog post to a markdown file in the current working directory:

```
blog-release-vX.Y.Z.md
```

The file should contain the full blog post. Append the metadata block as an
HTML comment at the end of the file (so it is invisible when rendered but
preserved for reference):

```markdown
<!--
Drafted from: generative-computing/mellea vX.Y.Z (RELEASE_URL)
Highlight PRs: #N, #N, #N  (score ≥ 50)
Mention PRs: #N, #N, ...    (score 10–49)
Skipped PRs: #N, #N, ...    (score < 10, not in post)
-->
```

After writing the file, confirm the path to the user.

---

## Related Skills

- `/get-blog-candidates` — rank PRs across multiple recent releases (not
  release-specific)
- `/write-technical-blog` — write a deep-dive post about a single feature
  rather than a release summary
