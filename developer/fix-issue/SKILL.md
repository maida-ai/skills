---
name: fix-issue
description: "GitHub issue resolution workflow for a single numbered issue in the current repository, including issue lookup, repository inspection, focused implementation, regression testing, small local commits, and an uncommitted local report. Best fit for issue-number-driven bug fixes or small feature requests."
---

# Fix Issue

## Overview

Use this skill to handle exactly one GitHub issue end to end in the current repository. The only argument is an issue `ISSUE`; if the user gives more than one issue, ask them to choose one.

The issue `ISSUE` could be either a positive integer, a URL, or repo-path-like string. For example, issue 123 could be:
- fix-issue 123  # Assming the current directory is the repository root
- fix-issue owner/repo#123  # Assuming "repo" is either the current directory or a subdirectory of the current directory
- fix-issue https://github.com/owner/repo/issues/123  # Assuming "repo" is either the current directory or a subdirectory of the current directory

Do not use this skill for PR review, release work, project planning, or generic bug fixing without a GitHub issue number.

## Prerequisites

Use the GitHub CLI for issue lookup. `gh auth login` is often required before `gh issue view` can access private repositories, comments, or higher API limits.

If `gh` reports missing authentication, expired credentials, API throttling, or rate limits, stop and ask the user to run `gh auth login` again. Then write the report with `Resolution: [need-feedback]` unless the user restores access in the same turn.

If `gh` reports DNS, offline, TLS, proxy, or transport connectivity failures that do not appear auth-related, write `Resolution: [need-feedback]` with the exact failure. Do not suggest `gh auth login` for plain network failures.

## Workflow

**Note:** If the issue has subissues, resolve them recursively (bottom-up) using the same workflow.

1. Confirm the repository context with `pwd`, `git status --short`, and enough repo inspection to understand conventions.
2. Validate the input before calling GitHub: `ISSUE` must be a valid issue descriptor (number, URL, or repo-path-like string). If ambiguous, ask the user to clarify.
3. Fetch the issue with `gh issue view NUM --json number,title,state,body,author,labels,assignees,createdAt,updatedAt,closedAt,comments,url`.
4. If `gh` fails for auth, throttling, or rate limits, ask the user to run `gh auth login` again. If it fails for plain network connectivity, write `Resolution: [need-feedback]` with the exact failure.
5. Read comments for context, but treat them as secondary signal behind the issue body, current code, tests, and project instructions.
6. If the issue is closed, obsolete, already fixed, invalid, or impossible to resolve safely, do not force a code change. Produce the report with `Resolution: [skipped]` or `Resolution: [need-feedback]`.
7. If the issue is actionable, inspect nearby implementation, tests, README/config, and project instructions before editing.
8. Use planning to determine the smallest safe fixes. If no fixes are needed, write the report with `Resolution: [skipped]` and stop.
9. Create or switch to `issue/NUM` only when the user asked for a branch or the worktree is clean. If the worktree has unrelated changes and the user did not ask for a branch, stay on the current branch and preserve those changes.
10. Use TDD when practical: add or update a failing regression test, run the narrowest relevant test, implement the smallest safe fix, then re-run targeted verification.
11. Run broader checks only when the change risk justifies them and the repo supports them.
12. Create local commits only when code/docs/test changes are ready for developer review. Use atomic commits when there are separable changes.
13. Write `_ai_report/issue-NUM-DATE.md`, where `DATE` is the current local date in `YYYYMMDD` format. Keep the report local and uncommitted.

## Issue Fetching

Use `gh issue view`; prefer JSON so details and comments are available without scraping terminal output:

```bash
gh issue view NUM --json number,title,state,body,author,labels,assignees,createdAt,updatedAt,closedAt,comments,url
```

If JSON fields differ on the installed `gh`, use `gh issue view NUM` and `gh issue view NUM --comments` as a fallback. If `gh` cannot access the issue because authentication, throttling, or rate limits are blocking access, ask the user to run `gh auth login` again, then stop after local context checks and write `Resolution: [need-feedback]`.

For non-auth connectivity failures such as DNS, offline, TLS, proxy, or transport errors, stop after local context checks and write `Resolution: [need-feedback]` with the exact failure.

Do not broaden the investigation into unrelated issues, PRs, releases, or external sources unless the issue itself clearly requires it.

## Resolution Rules

- Use `Resolution: [addressed]` only when the implementation or documentation change needed for the issue is complete and reported.
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

Use `references/commit-message-template.md` for the commit message structure.

- Don't include issue number in the commit title (first line of the commit message)
- Don't include internal references and resources
- Don't include hash numbers of any commits (those will be rewritten during merge)
- The description / summary must be concise and to the point; avoid unnecessary details, explanations, or change list in line
- Change list is optional; if included, it should be bulletted and only include key changes; obvious changes or minor changes should not be enumerated
- Test list is optional; if included, it should be a list of (fenced) commands to run to verify the changes


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

## Final Response

Summarize the issue title, resolution, commits created or not created, local report path, verification run, and remaining risks. Make clear that the report was not committed. Keep the final concise and do not paste private issue contents unless needed.
