---
name: self-improvement
description: "Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A command or operation fails unexpectedly, (2) User corrects Claude ('No, that's wrong...', 'Actually...'), (3) User requests a capability that doesn't exist, (4) An external API or tool fails, (5) Claude realizes its knowledge is outdated or incorrect, (6) A better approach is discovered for a recurring task. Also review learnings before major tasks."
---

# Self-Improvement Skill

Capture learnings during development and promote valuable ones into `CLAUDE.md`, project memory, or reusable skills. Log immediately — context is freshest right after the issue. Promote aggressively — learnings in `.learnings/` only help if they reach durable documents.

## Quick Reference

| Situation | Action |
|-----------|--------|
| Command/operation fails | Log to `.learnings/ERRORS.md` |
| User corrects you | Log to `.learnings/LEARNINGS.md` — category `correction` |
| User wants missing feature | Log to `.learnings/FEATURE_REQUESTS.md` |
| Knowledge was outdated | Log to `.learnings/LEARNINGS.md` — category `knowledge_gap` |
| Found better approach | Log to `.learnings/LEARNINGS.md` — category `best_practice` |
| Similar to existing entry | Link with `**See Also**`, bump priority if recurring |
| Broadly applicable learning | **Promote** to `CLAUDE.md` or project memory |
| Recurring pattern (3+ times) | **Extract** as a skill — see `references/skill-extraction.md` |
| Before a major task / after a feature | **Review** `.learnings/` — resolve, promote, or link entries |

## Setup

Create `.learnings/` in your project root (`mkdir -p .learnings`) with three files (or copy from `assets/`): `LEARNINGS.md`, `ERRORS.md`, `FEATURE_REQUESTS.md`.

**As a skill**: Place this folder under `skills/` or `~/.claude/skills/` — loaded automatically.
**As a hook**: See `references/hook-setup.md` for Claude Code hook configuration.
**Via CLAUDE.md**: Add a reminder to log to `.learnings/` when errors or corrections occur.

## Detection Triggers

Log when you notice any of these:

- **Corrections**: User says "that's wrong", "actually...", "that's outdated"
- **Knowledge gaps**: User provides info you didn't know, docs were outdated, API behaved unexpectedly
- **Errors**: Non-zero exit code, exception/stack trace, unexpected output, timeout
- **Feature requests**: "Can you also...", "I wish you could...", "Is there a way to..."

## Logging

Read `assets/LOGGING_FORMATS.md` for entry templates, ID format, priority/area tags, and resolution workflow.

**Short version**: Append an entry with ID (`LRN-YYYYMMDD-XXX`), priority, status (`pending`), a summary, details, suggested action, and metadata linking related files and entries.

## Promoting Learnings

Promotion is the payoff. Distill the learning into a concise rule and add it to the right target:

| Target | What Belongs There |
|--------|-------------------|
| `CLAUDE.md` | Project facts, conventions, gotchas — loaded every session |
| Project memory (`~/.claude/projects/*/memory/`) | Persistent context across sessions |
| New skill (`skills/<name>/SKILL.md`) | Reusable pattern — see `references/skill-extraction.md` |

Then update the original entry: set `**Status**: promoted` and add `**Promoted**: <target>`.

**Example** — verbose learning:
> Project uses pnpm workspaces. `npm install` failed. Lock file is `pnpm-lock.yaml`.

Promoted to `CLAUDE.md`:
```
## Build & Dependencies
- Package manager: pnpm (not npm) - use `pnpm install`
```

**Recurring patterns**: Before logging, search `.learnings/` for related entries. Link with `See Also`, bump priority. At 3+ occurrences, promote to `CLAUDE.md` or extract as a skill.
