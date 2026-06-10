# PR <PR_NUMBER> Commit <SHORT_COMMIT> Review

Generated: <DATE>
Repository: <OWNER>/<REPO>
PR: <PR_NUMBER>
Commit: <COMMIT_SHA>
Subject: <COMMIT_SUBJECT>
Report: `_ai_report/pr-<PR_NUMBER>-<SHORT_COMMIT>.md`
Result: <findings | nit-only | no findings>

## Commit Scope

<What this commit changes and why it appears atomic or not.>

## Existing Review Context

List each GitHub review thread for this commit once. Include replies under the same thread.

### Thread: <THREAD_ID>

Path: `<PATH>:<LINE>`
State: <resolved/unresolved>, <outdated/current>
Source: <URL>

Initial comment by <AUTHOR>:

> <COMMENT>

Replies:

- <AUTHOR>: <reply summary or quoted short reply>

Context decision: <resolved | still relevant | answered | outdated | not applicable>

## Findings

| Severity | Path | Line/Hunk | Summary |
|---|---|---|---|
| <blocker/major/minor/nit> | `<path>` | <line or hunk> | <summary> |

## Details

### <Severity>: <short title>

Path: `<PATH>:<LINE>`

Relevant changed lines or hunk:

```diff
<small relevant diff excerpt>
```

Comment:

<What is wrong, why it matters for this commit, and a suggested fix when useful.>

Related existing thread: <THREAD_ID or none>

## Atomicity Notes

<Whether this commit stands alone. Note missing tests, later-commit dependencies, or cross-commit coupling.>
