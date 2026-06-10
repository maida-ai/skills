# Maida AI Skills

This repository collects reusable AI-agent skills for Maida work. Skills are grouped by family in the source tree, then installed into an agent's local skills directory by skill name.

## Skill Families

- `developer/`: skills for engineering workflows inside code repositories.
- `product/`: reserved for skills about Maida product usage, customer workflows, and product operations.

Additional families can be added as the repository grows.

## Included Developer Skills

| Skill | Purpose | Source |
|---|---|---|
| `commit-stack-review` | Address GitHub PR review comments in the atomic commit where each comment belongs. | [maida#39](https://github.com/maida-ai/maida/pull/39) |
| `split-pr-stack` | Split oversized PR changes or large commits into smaller reviewable atomic commits. | [maida#40](https://github.com/maida-ai/maida/pull/40) |
| `fix-issue` | Resolve one GitHub issue locally with small commits and a local report. | `$HOME/.codex/skills/fix-issue` |

## Installation

Skills are installed by copying each skill folder into the local skills directory for your agent. The family directory is only for source organization; installed skills should be direct children of the target skills directory.

Install all developer skills for OpenAI Codex:

```bash
./scripts/install-skills developer
```

Install all developer skills for Claude Code:

```bash
./scripts/install-skills --target claude developer
```

Install one skill for Codex:

```bash
./scripts/install-skills developer/split-pr-stack
```

Replace an existing installed copy:

```bash
./scripts/install-skills --replace developer/split-pr-stack
```

Preview what would be installed:

```bash
./scripts/install-skills --dry-run developer
```

By default, the installer uses `$HOME/.agents/skills` for Codex and `$HOME/.claude/skills` for Claude Code. To install somewhere else:

```bash
./scripts/install-skills --dest /path/to/skills developer
```

## Basic Demo

After installation, ask Codex from a target repository:

```text
Use $split-pr-stack to split this large PR into reviewable atomic commits.
```

or:

```text
Use $commit-stack-review to address this PR's review comments while preserving its atomic commit stack.
```

Both skills are intentionally local-first: they create local report directories such as `_split_report/` and `_review_report/`, do not push rewritten history, and require explicit user direction before destructive or publishing operations.

## Validation

Run the local structural validator before publishing changes:

```bash
./scripts/validate-skills
```

The validator checks the portable Agent Skills shape: `SKILL.md` frontmatter, kebab-case names matching folder names, description length, concise skill bodies, executable bundled scripts, and referenced resource folders.
