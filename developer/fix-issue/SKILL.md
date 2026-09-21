---
name: fix-issue
description: "Resolve one GitHub issue and its subissues locally with focused changes, regression tests, reviewable commits, and an uncommitted report. Best for issue-number-driven fixes in the current repository."
---

# Fix Issue

## Overview

Use this skill for one root GitHub issue in the current repository (or a repository directly below the current directory). Recursively handle its subissues before resuming the parent. The only argument is an issue `ISSUE`; if the user supplies multiple root issues, ask them to choose one.

The issue `ISSUE` could be either a positive integer, a URL, or repo-path-like string. For example, issue 123 could be:
- fix-issue 123  # Assuming the current directory is the repository root
- fix-issue owner/repo#123  # Assuming "repo" is either the current directory or a subdirectory of the current directory
- fix-issue https://github.com/owner/repo/issues/123  # Assuming "repo" is either the current directory or a subdirectory of the current directory

Do not use this skill for PR review, release work, project planning, or generic bug fixing without a GitHub issue number.

## Prerequisites

Use the GitHub CLI for issue lookup. If a `git`, `gh`, or `gh stack` command fails, stop this workflow and report the exact command and error to the user. Write `Resolution: [need-feedback]` when the repository is available for a local report. Leave authentication, connectivity, repository state, and other CLI failures for the user to resolve; do not run login, install an extension, change credentials or Git configuration, retry, or switch to a different lookup path automatically. A command whose documented result is a nonzero status (such as a test intentionally expecting failure) is not a CLI failure.

## Workflow

**Subissues:** List direct subissues and recursively invoke `fix-issue` for each child, deepest first. Keep the parent pending until every child has been addressed or skipped as already complete. If a child needs feedback, stop and report that blocker for the parent. Use the `gh-stack` skill to arrange the issue branches in dependency order locally: child branches below the parent branch, with one branch per issue that needs changes. Read that skill before using `gh stack`; supply non-interactive arguments. Do not push, submit PRs, sync, rebase, rewrite history, or alter Git configuration. If a local stack cannot be created safely, stop and report the error. A subissue's completion must never close its parent.

1. Confirm the repository context with `pwd`, `git status --short`, and enough repo inspection to understand conventions.
2. Validate the issue descriptor (positive number, URL, or `OWNER/REPO#NUM`) and confirm that it identifies the repository being worked on.
3. Fetch the issue, its comments, and its direct subissues as described below. Read comments as secondary signal behind the issue body, current code, tests, and project instructions.
4. Resolve subissues bottom-up before doing the parent's implementation. Recheck the parent after the children: it may need no further change.
5. If the issue is closed, obsolete, already fixed, invalid, or impossible to resolve safely, do not force a code change. Report `[skipped]` or `[need-feedback]`.
6. For actionable work, inspect nearby implementation, tests, README/config, and project instructions. Identify the smallest safe fix.
7. Create or switch to `issue/NUM` only when the user asked for a branch or the worktree is clean. If unrelated changes exist and the user did not ask for a branch, stay on the current branch and preserve them. For subissues, use the local branch stack above.
8. Use TDD when practical: add or update a failing regression test, run the narrowest relevant test, implement the fix, then re-run targeted verification.
9. Run broader checks when the change risk justifies them and the repository supports them. Exercise the behavior at the interface named by the issue, not only through helpers.
10. Create local commits only when code/docs/test changes are ready for developer review. Use atomic commits when there are separable changes.
11. Perform the final review below, then write `_ai_report/issue-NUM-DATE.md` using the current local date. Keep the report local and uncommitted.

## Issue Fetching

For a number, use the current repository. For a URL or `OWNER/REPO#NUM`, select the indicated repository. From its working directory, use `gh repo view --json nameWithOwner` to confirm the owner and repository before any edits. Use `-R OWNER/REPO` with a number to avoid reading an issue from the wrong repository. Fetch details and comments as JSON:

```bash
gh issue view NUM -R OWNER/REPO --json number,title,state,body,author,labels,assignees,createdAt,updatedAt,closedAt,comments,url
```

List direct subissues with `gh api --paginate "repos/OWNER/REPO/issues/NUM/sub_issues" --jq '.[].html_url'`, then apply this workflow to each returned issue URL. Keep a separate branch, closing trailer, and report for each issue that requires work. If the API call fails, stop and report the error; do not assume the issue has no children.

Do not broaden the investigation into unrelated issues, PRs, releases, or external sources unless this issue or its subissues require it.

## Resolution Rules

- Use `Resolution: [addressed]` only when the issue's acceptance criteria are met and the evidence and limits are reported. Separate actual behavior from local simulation; if a criterion explicitly requires live verification that was not performed, use `[need-feedback]`.
- A parent may be `[addressed]` by completed subissues with no parent code change; its report must explain that result and note how the parent issue will be closed after the children land.
- Use `Resolution: [need-feedback]` when the issue is ambiguous, blocked on missing information, requires product judgment, or cannot be accessed.
- Use `Resolution: [skipped]` when the issue is stale, expired, already fixed, non-actionable, superseded, or unsafe to change.

## Commit Rules

- Create commits only for completed local changes that a developer can review.
- Keep commits atomic when one issue naturally splits into independent changes.
    - The key is to keep the commits reviewable and understandable on their own.
    - If a commit is very large (>1000 lines of change), split the commit into smaller commits
- Do not use `git push`, force-push, publish, deploy, delete branches, rewrite history, or change credentials.
- Do not use `git rm`. If deleting a tracked file appears necessary, stop and ask the user for explicit approval.
- Never revert unrelated user changes. If the worktree is dirty, inspect overlap and preserve unrelated edits.


## Commit Message

Read and follow `references/commit-message-template.md` for every commit. Its `**Changes**` and `**Tests**` sections are required.

- Don't include issue number in the commit title (first line of the commit message)
- Don't include internal references and resources
- Don't include hash numbers of any commits (those will be rewritten during merge)
- Keep the summary concise and explain the decision. Put key changes in bullets under `**Changes**`, and executed checks with results under `**Tests**`; if no check ran, state why.
- Put `Closes #NUM` only on the final, top commit for that completed issue, never on an earlier commit or a child commit for its parent. If a prerequisite commit is in another repository, it may use `Refs OWNER/REPO#NUM` for traceability; that does not replace the issue's `Closes` trailer.
- Do not create an empty commit solely to carry a closing keyword. If the parent needs no commit after its subissues, report how it was addressed and that its closure remains a followup.


## Report

If a commit was created, always create `_ai_report/issue-NUM-DATE.md` before finishing.
Create `_ai_report/` if missing.

The report must remain an uncommitted local artifact. If commits are created before the report, create the report afterward. If the report exists before committing, explicitly leave it unstaged.

Use `references/report-template.md` for the report structure. Include:

- detailed explanation of the change, grouped by commit when commits were created
- resolution status: `[addressed]`, `[need-feedback]`, or `[skipped]`
- verification commands and results
- followups, or `None`

- Never stage or commit generated `_ai_report/issue-*.md` files. The report is only for the developer to review before signing off on the skill's changes.
- Do not mention the generated report in commit messages or committed files.
- Before each commit, inspect the staged diff and ensure no `_ai_report/` path is staged.

## Final Review Before Sign-off

Re-read the issue's acceptance criteria and check each against the resulting behavior. Record what passed, what was simulated, what could not be verified, and the exact commands/results in the report. Re-run relevant checks if code changed since they last passed. Review the final diff and Git status, confirm the commits and their message structure, confirm each closing trailer belongs only to its own issue's final commit, and confirm every generated report exists and remains uncommitted. For a stack, check the local branch order with `gh stack view --json`. Stop and report any Git or GitHub CLI error rather than attempting repair.

## Final Response

Summarize the issue title, resolution, commits created or not created, local report path, verification run, and remaining risks. Make clear that the report was not committed. Keep the final concise and do not paste private issue contents unless needed.
