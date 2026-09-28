---
name: maida-debug-gate
description: "Explain a Maida PASS, FAIL, INCONCLUSIVE, setup error, or post-accept pending result and take the next safe local action. Use for first-run reports, behavioral regressions, or a gate that remains blocked after acceptance."
---

# Explain the result and recover

Follow the same [released onboarding route](https://maida.ai/docs/getting-started/) as setup. Inspect installed help and preserve the version and evidence semantics of the failing command. Maida 0.5.x and 0.6 have different single-run gate interfaces.

## Read the evidence first

Read the report, repository instructions, relevant source/configuration diff, baseline, policy and workflow. Identify the verdict, reason codes, expected/actual observations, coverage gaps and the evaluated commit. A correct answer can accompany changed behavior. A successful process does not imply PASS.

Give one next safe action appropriate to the state:

- **Setup error or no capture:** correct the named missing path, dependency, incomplete session or unsupported signal, then rerun the same task. Do not generate a new baseline from missing evidence.
- **INCONCLUSIVE:** explain which claim lacks evidence or has an infeasible budget. Preserve the stated requirement; obtain an approved feasible budget or a reviewed policy decision. Do not silently spend additional provider trials or lower thresholds.
- **FAIL:** connect the earliest changed tool, stop condition, loop or count to the source/configuration change. Reproduce in an isolated window and fix the unintended behavior.
- **PASS:** the observed checks passed; name unchecked behavior and remaining repository requirements. PASS is not complete release authorization.
- **Accepted baseline, fresh result pending:** the baseline commit changes the PR head. Inspect the accepted commit and the new head's check, required status and sticky comment. Dispatch success alone is not a gate verdict. A later push invalidates prior acceptance/results; use the Action's documented recovery route for the current head.

## Reproduce at the right layer

Keep the task/session grouping, agent/configuration identity, baseline hash and policy fixed. Use existing offline fixtures and a fresh `MAIDA_DATA_DIR`; do not mix baseline executions into the candidate window. Reuse the original command: `maida assert --baseline <path> --policy <path>` for a reviewed single captured execution on Maida 0.6 or newer, the compatibility capture-gate helper with explicit same-task mapping on Maida 0.5.x, `maida drift` for native windows with stable workflow names, `maida run` for traced Python entrypoints, or `maida scenario run` for a pinned coding-agent scenario within an authorized budget. Read `verdict` and reason codes in window/multi-trial JSON, or boolean `passed` and per-check `results` in single-run assertion JSON. Preserve that distinction rather than inferring approval from exit status.

Use `maida diff --baseline <path>` or the local viewer to investigate event order. The Maida 0.5.x legacy `maida assert` command can omit authored policy-v2 invariant metrics; do not replace the gate with it. Never replace a multi-trial or scenario gate with a single-run check. Reproduction must preserve what the original check evaluated.

## Fix or accept deliberately

For a regression, add a focused failing test, fix the responsible source behavior, and require FAIL → PASS with the same baseline/policy. Test harmless variance and relevant error paths. If reproduction disagrees, inspect version, capture coverage, grouping, environment and configuration before changing tolerances.

For an intentional change, show the structural diff and exact acceptance reason before mutation. Honor explicit acceptance already supplied for that evidence; otherwise ask only after preparing the reviewable result. `maida accept` takes different inputs for sampled reports and single runs: consult installed help, retain the original evidence semantics, and inspect the prior hash/provenance afterward. Acceptance does not authorize a cloud call or push, and cannot authorize a later unrelated commit.

Never delete failed checks, automatically rebaseline, suppress unknown evidence, or turn INCONCLUSIVE into approval. Report the root cause, coverage, exact commands, actual before/after verdicts and any unresolved external check. Keep payloads local and preserve unrelated user changes.
