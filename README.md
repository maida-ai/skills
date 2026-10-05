# Maida product skills

**Maida checks agent changes before merge.** This supported extension helps a coding agent adopt the [Maida engine and CLI](https://github.com/maida-ai/maida), use the [canonical runnable tutorials](https://github.com/maida-ai/maida-tutorials), and add the [GitHub PR gate](https://github.com/maida-ai/maida-assert).

## Product adoption skills

| Skill | Use it to |
|---|---|
| [maida-instrument-agent](product/maida-instrument-agent/) | Capture one coding-agent task or instrument a Python agent, then verify the observed evidence. |
| [maida-add-regression-gate](product/maida-add-regression-gate/) | Review candidate checks and a baseline, prove pass/fail/repair, then prepare CI when requested. |
| [maida-debug-gate](product/maida-debug-gate/) | Explain a result, investigate the regression, and take the next safe action. |

Use the skill for the stage you need; installing all three is optional. The engine owns the command and trace contracts. Skills guide adoption rather than implementing another gate.

## First time using Maida?

Start with the [released coding-agent walkthrough](https://maida.ai/docs/getting-started/) in your own Git repository. For Maida v0.6.1 with supported Claude capture, use Python 3.12–3.14:

```bash
uv tool install "maida-ai==0.6.1"

cd my-repo
maida init

# Approve the setup preview, then start a new coding-agent session.
# Complete one normal task and exit the session.

maida check
# Run the exact "View:" command printed by Maida.
```

The first report checks completion, observed loops, and guardrail events without a baseline or policy. Reviewed baseline and policy setup comes later. Other capture integrations use their own documented trace-reading route; see the [OpenCode plugin](https://github.com/maida-ai/opencode-plugin) for OpenCode sessions.

## Optional rehearsal: see the gate without a captured task

```bash
maida demo --regression
```

The canned, offline rehearsal shows a deliberate FAIL and PR-comment preview, then exits `0` when the expected failure is reproduced. It is optional practice, not evidence about your own agent. Runnable product examples live in [maida-tutorials](https://github.com/maida-ai/maida-tutorials).

## Install product skills

Skills use portable `SKILL.md` directories. Install individual folders as direct children of your client's skills directory; `product/` is source organization, not an installed directory level.

For Codex's built-in installer:

```text
Use $skill-installer to install these GitHub skills:
https://github.com/maida-ai/skills/tree/main/product/maida-instrument-agent
https://github.com/maida-ai/skills/tree/main/product/maida-add-regression-gate
https://github.com/maida-ai/skills/tree/main/product/maida-debug-gate
```

From a checkout, choose your client:

| Client | Command | Default destination |
|---|---|---|
| Codex | `./scripts/install-skills product` | `$HOME/.agents/skills` |
| Claude Code | `./scripts/install-skills --target claude product` | `$HOME/.claude/skills` |
| OpenCode | `./scripts/install-skills --target opencode product` | `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills` |

For project-local skills or another client, select its skills directory explicitly:

```bash
./scripts/install-skills --dest .agents/skills product
# Or use .claude/skills, .opencode/skills, or your client's directory.
```

Then ask your coding agent to use the relevant skill:

```text
Use maida-instrument-agent to capture and check one task in this repository.
```

See [product workflow guidance](product/README.md) for supported environments, coverage, and safety. Skills preserve existing settings and evidence and require explicit authorization for publishing, uploading traces, or accepting changed baselines.

## Contributor tooling

The `developer/` family contains generic contributor and repository-maintenance skills. These are separate from Maida's product adoption surface. Paths stay in place to preserve existing installs and developer workflows.

| Skill | Purpose |
|---|---|
| `fix-comments` | Address GitHub PR review comments in the atomic commit where each comment belongs. |
| `review-stack` | Review each stacked PR commit individually and write per-commit reports. |
| `split-pr-stack` | Split oversized PR changes or large commits into smaller reviewable atomic commits. |
| `fix-issue` | Resolve one GitHub issue locally with small commits and a local report. |

For Codex's built-in installer, use the individual contributor folders:

```text
Use $skill-installer to install these GitHub skills:
https://github.com/maida-ai/skills/tree/main/developer/fix-comments
https://github.com/maida-ai/skills/tree/main/developer/review-stack
https://github.com/maida-ai/skills/tree/main/developer/split-pr-stack
https://github.com/maida-ai/skills/tree/main/developer/fix-issue
```

From a checkout:

```bash
./scripts/install-skills developer
./scripts/install-skills --target claude developer
./scripts/install-skills --dest /path/to/tool/skills developer
```

Contributor examples:

```text
Use $split-pr-stack to split this large PR into reviewable atomic commits.
Use $fix-comments to address review comments while preserving the commit stack.
Use $review-stack to review PR 123 one atomic commit at a time.
```

These skills write local reports under `_ai_report/` and require explicit direction before destructive or publishing operations.

## Installer options

Install one product skill, preview a family, or update an installed copy:

```bash
./scripts/install-skills product/maida-debug-gate
./scripts/install-skills --dry-run product
./scripts/install-skills --replace product/maida-debug-gate
./scripts/install-skills --fail-fast product
```

Existing installs are skipped by default, replaced with `--replace`, or rejected with `--fail-fast`. Review an installed skill's local changes before replacing it.

## Versioning and validation

Install from a reviewed source revision. For numbered releases, follow the [Maida compatibility policy](https://github.com/maida-ai/maida/blob/main/CONTRIBUTING.md#versioning-and-compatibility): tested engine compatibility, independent patch releases, and immutable full tags. Matching version numbers alone do not establish feature parity.

Run the portable Agent Skills structural validator and dependency-free installer tests:

```bash
./scripts/validate-skills
./tests/install-skills.sh
```

See [workflow verification](product/README.md#workflow-verification) for offline released-engine checks.
