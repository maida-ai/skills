---
name: maida-debug-gate
description: "Diagnose a failing Maida behavioral regression gate from its report, reason codes, baseline, local trace, and source changes; then fix the regression or prepare an explicitly reviewed baseline update. Use when maida assert or maida-ai/maida-assert fails, a PR report shows changed agent structure, or a developer needs to decide whether changed behavior is a bug or intentional."
---

# Debug a Failing Maida Gate

Treat the gate report as evidence about changed execution structure, not as a generic test failure. Reproduce the failure locally, connect each structural change to source, and make the smallest justified response.

## Safety contract

- Keep traces and investigation local. Do not upload evidence, call cloud services or live models, or expose prompts, responses, tool payloads, environment variables, or credentials.
- Do not commit, push, create or edit pull requests, post replies, resolve comments, or publish anything without explicit authorization.
- Do not weaken policy, delete a check, suppress evidence, or update a baseline merely to turn the gate green.
- Treat `maida accept` as a consequential mutation. Never run it without explicit user confirmation of the intentional behavior change and the exact reason.
- Preserve unrelated changes and avoid running side-effecting agent tools. Use deterministic fixtures or replay paths for reproduction.

## Workflow

### 1. Start from the verdict

- Read the full Maida text, JSON, Markdown, or PR-comment report supplied by the user. Lead with the verdict, failed check names, stable reason codes, expected values, actual values, baseline path/run, and current run when present.
- If only a screenshot or excerpt is available, extract what is reliable and state what evidence is missing. Do not guess hidden checks.
- Read repository instructions, `git status`, the relevant source diff, agent entrypoint, tests, `.maida/policy.yaml`, workflow, and baseline before editing.
- Do not begin by changing code. First summarize what behavior changed and whether the run itself ended successfully.

### 2. Translate reason codes into hypotheses

Use reason codes to focus inspection:

| Reason code | Structural evidence | Inspect first |
|---|---|---|
| `step_count_exceeded` | More events than the accepted envelope | loop bounds, retries, duplicated callbacks, new branches |
| `tool_call_count_exceeded` | More tool invocations | retry policy, repeated planning, tool-result handling |
| `new_tool_path` | A tool absent from the baseline | routing changes, renamed tools, fallback selection |
| `loop_detected` or `cycle_detected` | Repeated call or multi-step cycle | stop conditions, state progress, error recovery |
| `terminal_state_missing` | Final status differs from policy | swallowed exceptions, missing return, guardrail abort |
| `guardrail_event_changed` | A runtime guardrail fired | underlying loop, call limit, duration, or event explosion |
| `cost_envelope_exceeded` | Token usage left the accepted envelope | extra model calls, prompt expansion, retries |
| `latency_envelope_exceeded` | Duration left the accepted envelope | added calls, serial work, slow fallback; verify deterministic noise |

These are starting hypotheses, not conclusions. A passing final answer does not override a structural regression.

### 3. Present the investigation plan

Before mutation, state:

- the reported changes and strongest source hypotheses;
- the checked-in baseline and policy paths;
- the deterministic offline command that can reproduce the agent behavior;
- the isolated `MAIDA_DATA_DIR` and exact `assert`, `diff`, and inspection commands;
- whether the current evidence is sufficient to distinguish regression from intent.

Do not run the CI workflow or a live provider to reproduce a PR failure.

### 4. Reproduce and inspect locally

Use one temporary data directory for the reproduction and Maida CLI commands:

1. Run the deterministic agent command on the failing code.
2. Run `maida assert --baseline <path> --format json` and confirm exit code `1` and the same reason codes. Omit the run ID so the local reproduction selects the latest run.
3. Run `maida diff --baseline <path>` to inspect counts, tool sequence, loops, status, tokens, and duration.
4. Use `maida export --out <temporary-file>` or the local viewer to inspect event ordering when aggregate evidence is insufficient. Keep exported payloads outside proposed repository changes and redact sensitive fixtures.
5. Compare the event sequence with the source diff and tests. Identify the earliest unexpected branch rather than blaming every downstream event.

If the failure cannot be reproduced, compare Maida versions, dependency locks, workflow command, policy precedence, environment, and nondeterministic fixture inputs. Do not broaden tolerances until the source of variance is understood.

### 5. Decide regression versus intentional change

Classify the evidence explicitly:

- **Regression:** behavior is accidental, violates policy, repeats work, loses a terminal state, adds an unintended tool, or lacks product/test justification. Fix source behavior and add a regression test.
- **Intentional change:** the new structure is required, its tool path and limits are understood, tests encode the new expectation, and the user confirms future runs should be compared against it.
- **Insufficient evidence:** reproduction is unstable, the baseline is stale for unknown reasons, or product intent is unresolved. Stop and request the missing decision; do not change policy or baseline.

Record the evidence for the classification, including final-answer parity when relevant. Never infer intent solely because the new output looks correct.

### 6. Apply the smallest safe response

For a regression:

1. Add a focused test that exposes the unexpected structure or missing stop condition.
2. Confirm the test and Maida assertion fail before the fix when feasible.
3. Correct the earliest responsible source behavior.
4. Rerun the deterministic agent and assertion; require exit code `0` without modifying the baseline or weakening policy.

For an intentional change:

1. Explain the structural change and show the current baseline diff.
2. Ask for explicit confirmation of the exact acceptance reason.
3. Only after confirmation, run `maida accept --baseline <path> --reason "<confirmed reason>"` without a run ID.
4. Inspect the baseline diff and acceptance metadata, rerun `maida assert`, and require exit code `0`.

Do not combine a source fix and baseline acceptance unless each has independent evidence and authorization.

### 7. Hand off for review

Show `git diff` and report the original reason codes, root cause, classification, response, before/after structural evidence, exact commands and exit codes, remaining risks, and manual-review files. Leave changes uncommitted unless the user separately requests a commit.
