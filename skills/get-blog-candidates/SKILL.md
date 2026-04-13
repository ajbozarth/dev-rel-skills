---
name: get-blog-candidates
description: >-
  Fetch and rank merged PRs from generative-computing/mellea by their likelihood
  of being good blog or demo candidates. Scores on: feat label/prefix, lines of
  code changed, and presence of docs/examples changes.
---

# Rank Mellea PRs for Blog/Demo Candidates

Fetch merged PRs from `generative-computing/mellea` for a given time window and
rank them by blog/demo potential.

## Usage

```
/get-blog-candidates [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--limit N]
```

Defaults: `--since` = Monday of current week, `--limit` = 30.

---

## Steps

### 1. Fetch merged PRs with file details

```bash
gh pr list \
  --repo generative-computing/mellea \
  --state merged \
  --search "merged:>SINCE_DATE" \
  --limit LIMIT \
  --json number,title,mergedAt,author,labels,url,additions,deletions,files
```

### 2. Score each PR

Apply the following scoring rubric (higher = better blog/demo candidate):

| Signal | Points |
|--------|--------|
| Title starts with `feat:` or `feat(` | **+40** |
| Label `enhancement` or `feature` | **+20** |
| Title starts with `fix:` | **+5** |
| Any changed file under `docs/examples/` | **+25** |
| Any changed file under `docs/docs/` | **+15** |
| Any changed `.md` file anywhere | **+10** |
| Net lines changed (additions + deletions) ≥ 500 | **+15** |
| Net lines changed ≥ 200 | **+10** |
| Net lines changed ≥ 50 | **+5** |
| Title starts with `chore:`, `ci:`, `build:`, or `fix: update github` | **-30** (infra noise) |
| Title starts with `docs:` (docs-only, no examples) | **-10** |

Compute `score` for each PR. Sort descending.

### 3. Output ranked table

Print a markdown table with columns:

| Rank | # | Title | Score | Signals |
|------|---|-------|-------|---------|

The **Signals** column should list which signals fired, e.g.:
`feat prefix, docs/examples touched, 1811 lines`

Then add a short section **"Top picks"** calling out the #1 and #2 PRs with a
one-sentence explanation of why each is a good candidate.

---

## Scoring Notes

- PRs with `docs/examples/` changes are high-value because they already have
  runnable demo material.
- Large line counts (≥ 500) indicate substantial new functionality.
- Infra PRs (`chore:`, `ci:`, `fix: update github action`) are penalized
  because they rarely make good blog content.
- If two PRs tie, prefer the one with `docs/examples/` changes.
