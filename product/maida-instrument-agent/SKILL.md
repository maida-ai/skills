---
name: maida-instrument-agent
description: "Capture one coding-agent task or add local Maida tracing to a Python tool-calling agent. Use for first-run Maida setup, capture, or instrumentation; choose the supported integration from the actual repository."
---

# Capture one useful task

Start from the [released coding-agent walkthrough](https://maida.ai/docs/getting-started/). Read only the stage needed for this task. Inspect installed help before selecting commands. Reviewed `init --from-run` / `--reviewed` requires Maida 0.6 or newer; Maida 0.5.x has a separate compatibility path.

## Inspect and choose

Read repository instructions, working-tree changes, package/lock files, the agent configuration and one relevant test. Identify a bounded task the owner already cares about, its expected result, and the capture surface. Briefly state the files and command you will use, then do the authorized work. Preserve existing user edits and hooks.

- **Coding agent:** use its existing native emitter or supported capture integration. The repository can be any language. Do not require Python instrumentation of the user's application. On Maida v0.6.1 with Claude capture, run `maida init` in the user's repository, review and approve the preview, then start a new coding-agent session. Preserve existing hooks. The [guided task](https://github.com/maida-ai/maida-tutorials/blob/main/guides/coding-agent.md) documents the released setup and recovery flow.
- **Python tool-calling agent:** install `maida-ai` into the project interpreter using its package manager; an isolated tool install does not expose the library. Wrap one complete invocation with `@trace` and record actual boundaries. Preserve return values, exceptions and existing callbacks.
- **Unsupported capture:** name the missing signal/integration and leave a concrete next step. Do not fabricate evidence or describe all coding agents as supported.

Supported integrations: local Claude Code hooks or OTel receiver; OpenCode native trace plugin; LangChain/LangGraph callback handler; OpenAI Agents SDK tracing processor; custom Python recorders. CrewAI support ends at v0.5.3 and the extra was removed from later development; inspect the installed release and compatibility guide before selecting the retained adapter.

## Capture and verify

Isolate offline verification with temporary HOME, cwd, and Maida storage. For the user's real v0.6.1 Claude task, reuse the initialized repository's capture scope; do not redirect it into an unrelated SDK store. For a Python agent or native emitter, use its documented storage selection consistently across capture and read commands. Preserve the user's HOME and existing storage. Keep telemetry local: an OTel receiver is a loopback process, not telemetry to Maida. Do not enable uploads or usage pings.

For coding-agent hooks, preserve existing settings, observe supported lifecycle events, and finish the session normally; SessionEnd imports the segment. Read the [hook integration](https://maida.ai/docs/claude-code/#passive-command-hook-fallback) for exact configuration. Hook evidence covers tool/lifecycle behavior; it does not establish full LLM, token, latency, or subagent coverage. Reuse recorded offline events for verification; an actual model run requires the user's existing authorization and budget.

For Python, use an existing offline fixture, supported adapter or fake provider. Add a regression test that proves output and exception behavior are unchanged, a complete trace is produced, and a fake secret is redacted. Never synthesize tool calls in production just to satisfy a policy.

Keep the first task small enough to finish in a minute or two, such as finding the test command and citing its configuration without edits. Aim for the first report in under 10 minutes for a bounded task; measure actual onboarding separately rather than presenting the target as observed performance. On Maida v0.6.1 with initialized Claude capture, run `maida check` and the exact viewer command it prints. It checks the latest repository task without a baseline or policy and ignores existing policy files. For another native emitter, validate and inspect its explicit trace ID using the integration guide; `maida check` does not select OpenCode or SDK runs. If an older installed release lacks `check`, use its explicit compatibility guide rather than silently using development commands. Explain that this checks only those recorded signals and does not establish answer correctness. If capture is empty, incomplete, or from another task, fix capture before generating a baseline. The demo explains the product; it is not evidence about the user's task.

## Finish this stage

Report the task, observed signals, coverage gaps, exact commands and results. Point to `maida-add-regression-gate` for reviewing baseline/policy candidates. Leave unrelated files alone. Commit, push, send messages, run hosted services, or accept changed baselines only within explicit user authorization already provided in the session; do not ask again for authorization already given.
