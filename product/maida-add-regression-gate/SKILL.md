---
name: maida-add-regression-gate
description: "Add a reviewed Maida baseline, policy-as-code configuration, and GitHub Actions behavioral regression gate to an already instrumented agent repository. Use when asked to establish known-good agent behavior, configure maida assert, scaffold maida-ai/maida-assert, or add Maida pre-merge CI protection."
---

# Add a Maida Regression Gate

Turn an existing deterministic Maida trace into a reviewable baseline and pre-merge gate. Use the CLI scaffolder as the source of truth, then replace its placeholders with the repository's real offline agent command and baseline path.

## Safety contract

- Keep runs and inspection local. Do not upload traces, invoke hosted models, expose credentials, or trigger GitHub Actions during setup.
- Do not commit, push, create or edit a pull request, or publish anything without explicit authorization. Adding workflow files locally is not authorization to activate them remotely.
- Never use `--force` over existing policy or workflow files without explicit approval. Merge with existing CI and preserve unrelated user changes.
- Never create a baseline from an unreviewed, failing, live-provider, or nondeterministic run.
- Never weaken policy or update a baseline merely to make a failure pass. Intentional baseline changes belong in the explicit `maida accept --reason` workflow after diagnosis.

## Workflow

### 1. Inspect the repository and current evidence

- Read repository instructions, `git status`, README, dependency and lock files, CI workflows, tests, agent entrypoint, and existing `.maida` files.
- Confirm Maida instrumentation encloses one complete agent invocation and identify a deterministic command that exercises it without network access or side effects.
- Confirm the existing package manager and the locally available `maida` version. Read that version's `maida init`, `baseline`, `assert`, and policy help or docs before relying on flags.
- If there is no deterministic known-good run, stop and explain what test fixture or instrumentation is missing. Do not substitute `maida demo`; the baseline must describe the target agent.

### 2. Present the change plan

Before mutation, state:

- the exact offline agent command and why it represents known-good behavior;
- the files `maida init --github` may create and any existing files that require a merge;
- the proposed baseline path and meaningful policy checks;
- the targeted verification commands and isolated `MAIDA_DATA_DIR`.

Call out that the generated workflow will not be run, committed, or pushed by this skill.

### 3. Scaffold safely

- Run `maida init --github` from the repository root without `--force`.
- Inspect `.maida/policy.yaml` and `.github/workflows/maida.yml`; do not assume creation means they are ready.
- Replace the workflow's placeholder `agent-script` with the real repository command or script input supported by the pinned action. Point `policy` at `.maida/policy.yaml` and, after baseline creation, point `baseline` at its checked-in path.
- Preserve the generated pinned action reference. Do not silently substitute a floating branch, an older major, or hand-written GitHub API logic.
- Ensure workflow permissions remain least-privilege: repository contents read access and pull-request write access only when the action must post its report.

### 4. Capture and review the initial baseline

Use one temporary data directory for the agent command and all following Maida commands so the user's real `~/.maida` state remains untouched:

1. Run the deterministic known-good agent once.
2. Run `maida list --json` and inspect the latest run's name, status, event counts, tools, and absence of sensitive fixture values.
3. Run `maida baseline --out .maida/baselines/<stable-agent-name>.json`. Do not extract or pass a run ID; `baseline` selects the latest run.
4. Inspect the baseline's structural signature: event counts, ordered tool calls, models, guardrail events, final status, and source run metadata.
5. Show the baseline diff before proceeding. If the run is incomplete, surprising, or contains sensitive data, stop, remove it from the proposed changes, and fix the instrumentation or fixture first.

The baseline is behavioral evidence, not a golden output assertion. Do not hand-edit its generated structural fields.

### 5. Make policy intentional

Review the starter tolerances against the observed trace. Enable only checks supported by the repository's expected behavior. Prefer explicit pre-merge invariants such as:

- `no_loops: true` when repeated behavior is never acceptable;
- `no_new_tools: true` when the approved tool set is stable;
- `no_guardrails: true` when guardrail activation means the run already degraded;
- `expect_status: ok` for successful agent workflows;
- hard caps when the team can justify stable ceilings.

Explain every non-default tolerance or cap. Avoid zero-tolerance duration or token limits for nondeterministic production agents unless the project explicitly requires them.

### 6. Reproduce the gate locally

Under the same isolated data directory:

1. Run the known-good agent again.
2. Run `maida assert --baseline .maida/baselines/<stable-agent-name>.json` without a run ID.
3. Confirm exit code `0`, the expected checks, and no unexpected ignored checks.
4. Run repository tests or validation for the policy and workflow when available.

Do not invoke the GitHub workflow, push a test branch, or make a provider call for verification. If the local assertion fails, diagnose it rather than loosening policy reflexively.

### 7. Hand off for review

Show `git diff` and summarize the baseline signature, policy decisions, generated workflow input, exact commands and exit codes, risks, and files requiring manual review. Leave all files uncommitted unless the user separately requests a commit.
