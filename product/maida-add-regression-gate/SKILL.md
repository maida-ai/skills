---
name: maida-add-regression-gate
description: "Turn captured coding-agent or Python-agent runs into a reviewed baseline and small behavioral policy, prove a local pass/fail/repair loop, and prepare CI when requested. Use for first Maida gates and onboarding."
---

# Protect one task

Use the [released coding-agent route](https://maida.ai/docs/getting-started/). Inspect the installed CLI version/help and repository instructions before editing. Use the installed version: Maida 0.6 and newer provide reviewed `init`; Maida 0.5.x needs the compatibility route below. Do not silently switch to development main.

## Establish the evidence

Inspect the working tree, actual task/entrypoint, existing `.maida` files, dependency lock and CI. Keep one known-good task/session group and agent/configuration identity. Isolate mutable trial state and offline fixture storage. For v0.6.1 Claude captures, keep the initialized repository's capture scope and the explicit trace ID from `maida check`; default SDK storage is separate. Verify a completed trace belongs to that task and has the signals the intended checks require. Use the user's existing capture; do not replace it with a demo. If the library is needed, install it in the project interpreter, not just as an isolated CLI.

State the concrete files and offline verification commands, then proceed within existing authorization. Preserve existing baseline/policy/workflow files and merge deliberately instead of using `--force`.

## Generate candidates, then review

If `maida init --help` includes `--from-run`, select the known-good trace explicitly. For v0.6.1 Claude capture, copy the trace ID from `maida check` and pass it to `maida init --from-run TRACE_ID`; `latest` uses SDK storage defaults and can select an unrelated run. For isolated SDK/native fixture storage, `maida init --from-run latest` remains available. This is reviewed baseline preparation after the first report, not capture setup. Check the printed workflow and trace ID, then inspect `.maida/starter/policy.yaml` and `review.json`. The draft is inactive. After explicit review, activate with `maida init --reviewed --reason "the accepted task requirements"`; Maida validates the edited candidates and records the accepted hashes.

For Maida 0.5.x, use `maida extract --window "$MAIDA_DATA_DIR/runs" --out maida-draft`. Read `draft.json`, select the matching workflow's printed `artifact_dir`, and inspect its `policy.yaml` and `baseline.json`. Follow the [compatibility walkthrough](https://github.com/maida-ai/maida-tutorials/blob/main/guides/coding-agent-0.5.md) for review and installation of the pair. Check grouping, provenance and observed tools in either path; do not silently combine unrelated sessions.

Propose at most a few checks the owner can understand. Successful completion, no loops and no guardrail aborts can be candidate invariants when supported by the observations. Remove incidental path, timing and count requirements unless the user adopts them. Do not invent forbidden tools the repository lacks. One successful trace is sampled evidence, not a reliability guarantee. Do not lower an adopted threshold or change budgets to manufacture a PASS.

Present the proposed checks and their evidence. An instruction to set up Maida does not itself accept inferred contracts. Prepare the draft first; require explicit owner acceptance before activating the reviewed pair at `.maida/policy.yaml` and `.maida/baselines/agent.json`. Honor specific acceptance already given in this session, and record its reason in the reviewable change.

## Prove the local loop

After acceptance, replay the known-good task with fresh mutable state, keeping baseline and candidate runs in separate windows. Select the runner that matches the evidence:

- A fresh coding-agent capture on Maida 0.6 or newer: confirm it performed the same task from the same starting state, then `maida assert TRACE_ID --baseline .maida/baselines/agent.json --policy .maida/policy.yaml --format json`, using that fresh capture's explicit trace ID (from `maida check` for v0.6.1 Claude capture). Bare `assert` retains SDK storage defaults. This evaluates one observed execution, not a population claim.
- A fresh capture on Maida 0.5.x: use the [compatibility capture-gate helper](https://github.com/maida-ai/maida-tutorials/blob/main/onboarding/gate_capture.py) from a reviewed tutorials checkout. Run it with `uv run --no-project --with "maida-ai==0.5.3" python /path/to/maida-tutorials/onboarding/gate_capture.py --window "$MAIDA_DATA_DIR/runs" --baseline .maida/baselines/agent.json --policy .maida/policy.yaml --same-task --format json`. Confirm the sessions represent the same task first. The helper records the identity mapping and baseline hash without rewriting source artifacts. The released capture integration uses a different run name per session, so plain `drift` cannot match the new session automatically. The 0.5.x legacy `assert` omits policy-v2 invariants; its no-baseline flags are suitable only for the earlier first-signal check.
- A native trace window with stable workflow names: `maida drift --window "$MAIDA_DATA_DIR/runs" --baseline .maida/baselines/agent.json --policy .maida/policy.yaml --format json`.
- A traced Python script: `maida run agent.py --trials 1 --baseline .maida/baselines/agent.json --policy .maida/policy.yaml --format json`, using the project's environment. One trial is for the initial invariant-only rehearsal; statistical policies retain their configured feasible budgets.
- A pinned coding-agent task with an existing scenario manifest: `maida scenario run`, within the authorized execution budget.

Read the command's report contract: single-run `assert --format json` reports boolean `passed` and per-check `results`; window and multi-trial gate reports expose `verdict`. Do not look for a `verdict` field in an assertion report or replace a multi-trial claim with that single-run boolean. Exit `0` can mean PASS or INCONCLUSIVE; never describe the latter as a passed check. Require a real PASS for the good task, FAIL for an intentionally regressed disposable fixture, and PASS after repair without loosening policy or replacing the baseline. Setup failure is distinct: repair missing capture, dependencies or paths and rerun. Keep payloads local and do not call a live model merely for verification.

## Add CI only for the requested boundary

For Maida 0.6 and newer, a reviewed starter plus `maida init --github --agent-script path/to/real_agent.py` generates a workflow for an existing traced Python entrypoint and its declared dependencies. Inspect optional dependencies and runtime configuration before enabling it. Maida 0.5.x generates placeholders that must be filled manually. In either case, use the actual entrypoint, dependencies, baseline and policy, and pin a reviewed compatible Action commit. Existing workflows need a focused merge. A stored trace alone does not provide a runnable coding-agent scenario.

Follow the [Action's setup contract](https://github.com/maida-ai/maida-assert/blob/main/docs/usage.md#blocking-mode-and-required-repository-settings): trusted base policy, blocking INCONCLUSIVE, workflow review protection, exact-head configuration acceptance, and a fresh verdict after a baseline commit. Do not infer enforcement from generated YAML or local tests. The actual protected-consumer acceptance/dispatch loop must have recorded remote evidence before claiming it works. Prepare local files without pushing or changing repository settings unless authorized.

Report the reviewed checks, observed coverage, before/after verdicts, exact commands, and the next safe action. Preserve session authorization for commits and other mutations instead of asking repeatedly.
