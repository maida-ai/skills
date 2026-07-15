# Maida Product Skills

This family contains portable Agent Skills for the developer-led Maida workflow:

1. `maida-instrument-agent` inspects an agent repository and adds local Maida tracing.
2. `maida-add-regression-gate` creates and reviews a baseline, policy, and GitHub gate.
3. `maida-debug-gate` explains a failing behavioral regression report and guides the smallest safe response.

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
