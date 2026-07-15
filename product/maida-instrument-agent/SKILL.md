---
name: maida-instrument-agent
description: "Inspect a Python agent repository and add the smallest reviewable Maida instrumentation using a supported framework adapter or the core tracing API. Use when asked to trace, instrument, or capture the structural behavior of a LangChain/LangGraph, OpenAI Agents SDK, CrewAI, or custom Python agent with Maida."
---

# Instrument an Agent with Maida

Add local Maida tracing without changing the agent's intended behavior. Prefer an existing framework adapter, preserve repository conventions, and prove that a deterministic run produces inspectable structural evidence.

## Safety contract

- Keep all traces local. Do not upload traces, call cloud services for Maida, enable telemetry, or print secrets or full sensitive payloads.
- Do not run an agent that can call a model, network service, or side-effecting tool unless the user explicitly authorizes that run. Prefer existing fake, stubbed, or offline tests.
- Do not commit, push, create or edit a pull request, or publish anything without explicit authorization. A request to instrument does not grant that authorization.
- Preserve unrelated changes. Never overwrite existing tracing or configuration silently.
- Keep redaction enabled for verification.

## Workflow

### 1. Inspect before editing

- Read repository agent instructions, `git status`, the tree, README, dependency and lock files, tests, and the actual agent entrypoint.
- Identify the language, package manager, framework and version, invocation path, existing callbacks/hooks, and current test strategy. Do not infer them from the request alone.
- Search for existing Maida instrumentation and configuration. If the entrypoint is not Python, or the installed framework/version has no supported integration, explain the mismatch and stop before editing instead of inventing an adapter.
- Inspect the installed Maida API or the repository's pinned documentation when versions may differ. Do not assume examples from another version are valid.

### 2. Select the narrowest integration

Use the first matching path:

- **LangChain or LangGraph:** wrap the entrypoint with `@trace`, create `maida.integrations.LangChainCallbackHandler`, and pass it through the framework's existing callback configuration.
- **OpenAI Agents SDK:** import `maida.integrations.openai_agents` to register its tracing processor and wrap the entrypoint with `@trace`.
- **CrewAI:** import `maida.integrations.crewai` to register execution hooks and wrap the crew or flow entrypoint with `@trace`.
- **Custom Python loop:** wrap the real run boundary with `@trace` and place `record_llm_call`, `record_tool_call`, and `record_state` at the existing execution boundaries. Do not fabricate events merely to satisfy a test.

Adapters require an active Maida run. Put the trace boundary around one complete agent invocation, not around individual helper calls. Keep framework-specific data in adapter metadata rather than changing Maida's event model.

### 3. Present the change plan

Before mutation, state:

- the detected entrypoint and integration path;
- the dependency command, source files, and tests to change;
- the exact offline verification commands and isolated trace directory;
- any uncertainty or behavior that needs user confirmation.

Use the repository's existing package manager. Add only the matching `maida-ai` dependency or extra; do not switch package managers or add unrelated packages.

### 4. Implement a reviewable slice

- Add or update a focused test first when practical. The test must fail without the instrumentation and use fake/local models and stub tools.
- Add the trace boundary and adapter registration with the fewest necessary source edits.
- Preserve function signatures, return values, exception behavior, tool ordering, and existing callback configuration.
- Route payloads through Maida's recorder or adapter so its redaction and truncation remain active. Do not add ad hoc payload logging.

### 5. Verify local evidence

Use a temporary `MAIDA_DATA_DIR` for tests and smoke runs so the user's real `~/.maida` state is untouched. Run the narrow test first, then the repository's broader configured checks when proportionate. For an authorized deterministic invocation, verify:

- the agent result and error behavior are unchanged;
- `maida list --json` shows one completed run under the isolated data directory;
- the trace contains the expected LLM/tool structure and no raw secret fixture;
- an error-path test still writes terminal evidence and propagates the original failure.

Do not treat an import-only test as sufficient evidence. Do not make a live provider call just to obtain a trace.

### 6. Hand off for review

Show `git diff` and summarize the structural evidence, commands run, results, risks, and files needing manual review. Leave changes uncommitted unless the user separately requests a commit.
