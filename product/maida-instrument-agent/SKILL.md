---
name: maida-instrument-agent
description: "Capture one coding-agent task or add local Maida tracing to a Python tool-calling agent. Use for first-run Maida setup, capture, or instrumentation; choose the supported integration from the actual repository."
---

# Capture one useful task

Start from the [released coding-agent walkthrough](https://maida.ai/docs/getting-started/). Read only the stage needed for this task. Inspect installed help before selecting commands. Reviewed `init --from-run` / `--reviewed` requires Maida 0.6 or newer; Maida 0.5.x has a separate compatibility path.

## Inspect and choose

Read repository instructions, working-tree changes, package/lock files, the agent configuration and one relevant test. Identify a bounded task the owner already cares about, its expected result, and the capture surface. Briefly state the files and command you will use, then do the authorized work. Preserve existing user edits and hooks.

- **Coding agent:** use its existing native emitter or supported capture integration. The repository can be any language. Do not require Python instrumentation of the user's application. The [guided task](https://github.com/maida-ai/maida-tutorials/blob/main/guides/coding-agent.md) includes a safe additive capture-hook installer.
- **Python tool-calling agent:** install `maida-ai` into the project interpreter using its package manager; an isolated tool install does not expose the library. Wrap one complete invocation with `@trace` and record actual boundaries. Preserve return values, exceptions and existing callbacks.
- **Unsupported capture:** name the missing signal/integration and leave a concrete next step. Do not fabricate evidence or describe all coding agents as supported.

Supported integrations: local Claude Code hooks or OTel receiver; OpenCode native trace plugin; LangChain/LangGraph callback handler; OpenAI Agents SDK tracing processor; custom Python recorders. CrewAI support ends at v0.5.3 and the extra was removed from later development; inspect the installed release and compatibility guide before selecting the retained adapter.

## Capture and verify

Use a temporary `MAIDA_DATA_DIR` shared by the agent process and every Maida command. Preserve the user's HOME and existing storage. Keep telemetry local: an OTel receiver is a loopback process, not telemetry to Maida. Do not enable uploads or usage pings.

For coding-agent hooks, preserve existing settings, observe supported lifecycle events, and finish the session normally; SessionEnd imports the segment. Read the [hook integration](https://maida.ai/docs/claude-code/#passive-command-hook-fallback) for exact configuration. Hook evidence covers tool/lifecycle behavior; it does not establish full LLM, token, latency, or subagent coverage. Reuse recorded offline events for verification; an actual model run requires the user's existing authorization and budget.

For Python, use an existing offline fixture, supported adapter or fake provider. Add a regression test that proves output and exception behavior are unchanged, a complete trace is produced, and a fake secret is redacted. Never synthesize tool calls in production just to satisfy a policy.

Keep the first task small enough to finish in a minute or two, such as finding the test command and citing its configuration without edits. Aim for the first report within 10–15 minutes including setup; this is a target, not a measured activation claim. Run `maida list` in the capture environment, then `maida assert --expect-status ok --no-loops --no-guardrails` for a first check of the observed completion, loops and guardrails. No baseline is needed. Inspect any existing `.maida/policy.yaml` first because `assert` also loads it. Explain that this checks only those recorded signals and does not establish answer correctness. If capture is empty, incomplete, or from another task, fix capture before generating a baseline. The demo explains the product; it is not evidence about the user's task.

## Finish this stage

Report the task, observed signals, coverage gaps, exact commands and results. Point to `maida-add-regression-gate` for reviewing baseline/policy candidates. Leave unrelated files alone. Commit, push, send messages, run hosted services, or accept changed baselines only within explicit user authorization already provided in the session; do not ask again for authorization already given.
