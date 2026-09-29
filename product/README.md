# Maida Product Skills

Start with the [released coding-agent walkthrough](https://maida.ai/docs/getting-started/). These portable skills support one stage at a time; you do not need to install or read all three before trying Maida. The skills select the installed command contract: a first report before baseline setup, reviewed `init` on Maida 0.6 and newer, and a separate Maida 0.5.x compatibility route.

This family contains portable Agent Skills for the developer-led Maida workflow:

1. `maida-instrument-agent` captures a coding-agent task or adds local Python tracing.
2. `maida-add-regression-gate` derives candidate checks, obtains review, proves pass/fail/repair, and prepares CI when requested.
3. `maida-debug-gate` explains every first-run result and guides the next safe action.

## Supported environments

The canonical skill source is this directory. Do not maintain environment-specific copies.

| Environment | Global installation | Project-local installation |
|---|---|---|
| OpenAI Codex | `$HOME/.agents/skills` | `.agents/skills` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |
| OpenCode | `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills` | `.opencode/skills` |

The skills use the portable `SKILL.md` format. `agents/openai.yaml` supplies optional Codex UI metadata without changing the workflow for other clients.

## Shared safety contract

Every product skill must:

- inspect repository instructions, the working tree, entrypoints, dependency files, and existing tests before proposing edits;
- state the files and commands it intends to change or run before mutation;
- preserve unrelated user changes and keep diffs focused and reviewable;
- keep traces and generated artifacts local, isolate test storage, and avoid live model or service calls in verification;
- redact secrets and avoid printing prompts, responses, tool payloads, environment variables, or credentials unnecessarily;
- require explicit user authorization before committing, pushing, creating or editing pull requests, uploading traces, using cloud services, or accepting a changed baseline;
- verify the narrow behavior first, then run the broader checks supported by the repository;
- report exact commands, results, remaining risks, and files requiring manual review.

## Product boundaries

These skills help a coding agent perform explicit Maida setup and diagnosis. They do not silently inject instrumentation, mutate repositories without a reviewable plan, turn Maida into a generic coding-agent platform, or introduce hosted telemetry. Maida remains a local-first, pre-merge behavioral regression gate.

## Workflow verification

Keep a reviewed maida-tutorials checkout alongside this repository, or set `MAIDA_TUTORIALS_PATH` to its location; the fresh-session test checks for the compatibility helper and uses current `assert` on Maida 0.6. Run `UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with "maida-ai==0.6.0" python -m unittest discover -s tests -p "test_product_workflows.py" -v`. The tests use isolated temporary repositories and the published package to exercise capture, reviewed initialization, PASS, deliberate FAIL, repair and missing evidence. These scripted offline checks do not measure human unassisted activation or establish live GitHub protection.
