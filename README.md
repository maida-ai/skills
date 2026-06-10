# Maida AI Skills

This repository collects reusable AI-agent skills for Maida work. Skills are grouped by family in the source tree, then installed into an agent's local skills directory by skill name.

## Skill Families

- `developer/`: skills for engineering workflows inside code repositories.
- `product/`: reserved for skills about Maida product usage, customer workflows, and product operations.

Additional families can be added as the repository grows.

## Included Developer Skills

| Skill | Purpose |
|---|---|
| `commit-stack-review` | Address GitHub PR review comments in the atomic commit where each comment belongs. |
| `split-pr-stack` | Split oversized PR changes or large commits into smaller reviewable atomic commits. |
| `fix-issue` | Resolve one GitHub issue locally with small commits and a local report. |

## Installation

Skills are installed by copying each skill folder into the local skills directory for your agent. The family directory is only for source organization; installed skills should be direct children of the target skills directory.

### OpenAI Codex

Inside Codex, use the built-in skill installer with the GitHub skill folders:

```text
Use $skill-installer to install these GitHub skills:
https://github.com/maida-ai/skills/tree/main/developer/commit-stack-review
https://github.com/maida-ai/skills/tree/main/developer/split-pr-stack
https://github.com/maida-ai/skills/tree/main/developer/fix-issue
```

For local development from a checkout:

```bash
./scripts/install-skills developer
```

By default, this installs to `$HOME/.agents/skills`.

### Claude Code

Claude Code loads personal skills from `$HOME/.claude/skills`. From a checkout:

```bash
./scripts/install-skills --target claude developer
```

You can also ask Claude Code to clone this repository and run that installer:

```text
Clone https://github.com/maida-ai/skills and run ./scripts/install-skills --target claude developer.
```

For project-local Claude Code skills, copy the desired skill folders into `.claude/skills/` in the target repository.

### Generic Agent Skills Clients

For tools that support the Agent Skills directory format but use a different skills directory, install with `--dest`:

```bash
./scripts/install-skills --dest /path/to/tool/skills developer
```

If the tool has its own GitHub skill installer, point it at the individual skill folders under:

```text
https://github.com/maida-ai/skills/tree/main/developer/
```

### Local Installer Options

Install one skill:

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

## Basic Demo

After installation, ask Codex from a target repository:

```text
Use $split-pr-stack to split this large PR into reviewable atomic commits.
```

or:

```text
Use $commit-stack-review to address this PR's review comments while preserving its atomic commit stack.
```

These skills are intentionally local-first: they write reports under `_ai_report/`, do not push rewritten history, and require explicit user direction before destructive or publishing operations.

## Validation

Run the local structural validator before publishing changes:

```bash
./scripts/validate-skills
```

The validator checks the portable Agent Skills shape: `SKILL.md` frontmatter, kebab-case names matching folder names, description length, concise skill bodies, executable bundled scripts, and referenced resource folders.
