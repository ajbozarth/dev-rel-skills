# dev-rel-skills

A collection of Claude Code agent skills for developer relations work. These skills automate the repetitive parts of dev-rel: finding what's worth writing about, drafting blog posts, and promoting content on social media.

## Skills

### `/get-blog-candidates`

Fetches merged PRs from a GitHub repo and ranks them by blog/demo potential. Scores each PR on signals like `feat:` prefix, lines changed, and whether it touched `docs/examples/`. Outputs a ranked table with a "Top picks" callout so you can quickly decide what to write about next.

```
/get-blog-candidates [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--limit N]
```

### `/release-blog`

Takes the latest GitHub release, scores all its PRs by blog-worthiness, identifies a narrative theme, and drafts a full release blog post. Highlight-tier PRs get their own sections with before/after code; lower-scoring PRs are grouped into an "Other Improvements" section. Writes the result to `blog-release-vX.Y.Z.md`.

```
/release-blog [--tag vX.Y.Z] [--repo owner/repo]
```

### `/write-technical-blog`

A structured guide for writing a deep-dive technical blog post about a single feature, capability, or PR. Covers post types (narrative, feature announcement, tutorial, retrospective), required structure (hook → motivation → walkthrough → trade-offs → CTA), code example rules, tone guidelines, and an SEO checklist. Writes the draft to a `blog-<slug>.md` file.

```
/write-technical-blog [topic or PR number or description]
```

### `/write-tweet`

Writes high-engagement tweets or threads about technical content. Classifies the announcement type (new feature, performance improvement, major release, etc.), applies opening formulas that stop the scroll, and structures multi-tweet threads so each tweet stands alone. Writes output to `tweet-<slug>.md` with character counts, media recommendations, and an alternative opener.

```
/write-tweet [topic, PR number, path/to/post.md, or "thread about X"]
```

### `/validate-snippets`

Extracts every fenced code block from a markdown file, executes each one, and reports which pass, fail, or were skipped. Supports Python, Go, JavaScript, TypeScript, and shell. Non-code blocks (JSON, YAML, output, etc.) are automatically skipped. Writes a detailed report and offers to fix failing snippets in place.

```
/validate-snippets <path/to/file.md>
```

### `/de-llmify`

Edits a piece of writing to remove patterns commonly associated with LLM-generated text — hollow openers, filler transitions, over-explained structure, hedge stacking, and corporate-speak. Based on Kobak et al. 2024 research and developer community observations. Pass a file path or inline text.

```
/de-llmify [path/to/file.md or inline text]
```

## Setup

Add this repo path to `permissions.additionalDirectories` in `~/.claude/settings.json`:

```json
"permissions": {
  "additionalDirectories": [
    "/path/to/dev-rel-skills"
  ]
}
```

Claude Code will automatically discover and load all skills from `.claude/skills/` in this repo, alongside any existing skills you already have configured.

**What gets loaded:** skills only. Hooks, subagents, and commands in `.claude/` are ignored. CLAUDE.md/rules are also ignored unless `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is set.

See the [Claude Code permissions docs](https://code.claude.com/docs/en/permissions#working-directories) and [skills docs](https://code.claude.com/docs/en/skills#skills-from-additional-directories) for more detail.

## Workflow

A typical dev-rel workflow using these skills:

1. **Find candidates** — run `/get-blog-candidates` to see what merged recently and what's worth writing about
2. **Draft content** — use `/release-blog` for release summaries or `/write-technical-blog` for deep dives on a single feature
3. **Validate** — run `/validate-snippets` on the draft to make sure all code examples actually work
4. **Promote** — run `/write-tweet` on the resulting blog post file to generate a thread that drives readers to it
5. **Polish** — run `/de-llmify` on any generated content to remove AI writing tells before publishing