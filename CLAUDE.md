# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of Claude Code agent skills for developer relations work. Skills are defined as SKILL.md files under `.claude/skills/` and are invoked via `/skill-name` commands. There is no build system, test suite, or runtime — the "application" is the prompt instructions themselves.

## Skill Architecture

Each skill lives in `.claude/skills/<skill-name>/SKILL.md`. Skills are designed to work as a pipeline:

1. `/get-blog-candidates` — Fetches merged PRs from `generative-computing/mellea`, scores each by blog potential, and outputs a ranked table
2. `/release-blog` — Drafts a full release post from the latest GitHub release, scoring PRs into Highlight (≥50), Mention (10–49), and Skip (<10) tiers
3. `/write-technical-blog` — Deep-dive post guide drawing on best practices from Stripe, GitHub, Cloudflare, HashiCorp, and Google engineering blogs
4. `/write-tweet` — Generates tweet threads with proven opening formulas and per-announcement-type content rules

Skills can be used independently but typically flow sequentially: discover → draft → promote.

## External Dependency

All skills that fetch GitHub data rely on the `gh` CLI being installed and authenticated. Skills use `gh pr list`, `gh pr view`, `gh release view`, and `gh api`.

## Output Files

Skills write their output to the working directory:
- Release blog posts → `blog-release-vX.Y.Z.md`
- Feature blog posts → `blog-<slug>.md`
- Tweet threads → `tweet-<slug>.md`

See `demos/` for real examples of each output type.

## Adding or Modifying Skills

When editing SKILL.md files, the default target repo is `generative-computing/mellea`. Update the repo reference in the relevant SKILL.md if repurposing a skill for a different project.
