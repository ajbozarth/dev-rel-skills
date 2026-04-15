---
name: research-project
description: >-
  Research a GitHub project to build context for content creation. Fetches
  README, repo metadata, recent releases, and key stats to produce a
  structured project summary.
---

# Research Project

Gather comprehensive context about a GitHub project to inform downstream
content creation (blog posts, tweets, release notes).

## Usage

```
/research-project --repo owner/repo
```

Defaults:
- `--repo` = auto-detected from the current working directory's git remote

---

## Steps

### 1. Determine the target repo

If `--repo` was passed, use it. Otherwise auto-detect from the working
directory:

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

If that fails, ask the user for `owner/repo`.

### 2. Fetch repo metadata

Run:

```bash
gh repo view {repo} --json name,description,url,homepageUrl,stargazerCount,forkCount,primaryLanguage,languages,repositoryTopics,licenseInfo,createdAt,pushedAt,isArchived
```

Extract:
- **Name and description** — what the project calls itself
- **Stars / forks** — scale/adoption signal
- **Primary language and other languages** — tech stack
- **Topics** — category tags
- **License** — open-source status
- **Created / last push** — maturity and activity signals

### 3. Fetch the README

```bash
gh api repos/{owner}/{repo}/readme --jq .content | base64 -d
```

Read the README content. Extract:
- **What it does** — one-paragraph summary
- **Key features** — bullet list of main capabilities
- **Installation / quickstart** — how users get started
- **Target audience** — who is this for

### 4. Fetch recent releases

```bash
gh release list --repo {repo} --limit 5
```

For the latest release, also fetch details:

```bash
gh release view --repo {repo} --json tagName,name,body,publishedAt,isPrerelease
```

Extract:
- **Release cadence** — how often releases ship
- **Latest version and date**
- **Highlights from release notes** — what changed recently

### 5. Fetch contributor and activity signals

```bash
gh api repos/{owner}/{repo}/contributors?per_page=5 --jq '.[].login'
```

```bash
gh api repos/{owner}/{repo}/stats/commit_activity --jq '.[-4:][] | .total'
```

Note the top contributors and recent commit frequency.

### 6. Write the research summary

Produce a markdown file named `project-research-{repo-name}.md` with this structure:

```markdown
# Project Research: {project name}

## Overview
{1-2 paragraph summary: what it is, who it's for, what problem it solves}

## Key Facts
- **Repo**: {owner/repo}
- **URL**: {url}
- **Stars**: {count} | **Forks**: {count}
- **Language**: {primary} (also: {others})
- **License**: {license}
- **Created**: {date} | **Last push**: {date}
- **Topics**: {topic list}

## Core Capabilities
{Bullet list of the project's main features and capabilities, derived from README}

## Getting Started
{Brief quickstart — how to install and first usage, from README}

## Recent Activity
- **Latest release**: {tag} ({date})
- **Release cadence**: {roughly how often}
- **Recent highlights**: {key changes from latest release notes}

## Top Contributors
{List of top 5 contributors}

## Content Angles
{2-3 suggested angles for blog posts or social content, based on what makes
this project interesting — unique features, recent momentum, ecosystem fit}
```

### 7. Constraints

- Keep the summary under 1000 words — this is context for other skills, not a published document.
- Stick to facts from the repo data. Do not speculate about features not documented in the README or releases.
- If any `gh` command fails (private repo, rate limit), note what was unavailable and continue with what you have.
- Do NOT read the full source code. The README and releases are sufficient.
