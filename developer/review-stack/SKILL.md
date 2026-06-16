---
name: review-stack
description: GitHub PR review workflow for reviewing each stacked commit in a numbered pull request as a functionally atomic change, mapping existing review threads and replies to specific commits, and writing one severity-labeled local report per commit. Best fit for PRs where commits are intended to be independently reviewable.
---

# Review Stack

Use this skill to review a stacked GitHub PR one commit at a time. Treat each commit as functionally atomic unless the evidence shows otherwise.

## Resources

- `<path-to-skill>/scripts/get-stack-review-context`: fetch PR commits and deduplicated review threads grouped by commit.
- `<path-to-skill>/scripts/pr-stack-review.graphql`: GraphQL query used by the helper.
- `<path-to-skill>/scripts/group-stack-review.jq`: jq transformer used by the helper.
- `<path-to-skill>/assets/commit-review-template.md`: report shape for each commit.

Do not duplicate review comments: a GitHub review thread appears once, with replies nested as context.

## Workflow

1. Validate that the user provided exactly one positive PR number.
2. Identify `OWNER`, `REPO`, `PR`, `BASE_REF`, and a local PR head ref.
3. Fetch the base branch and PR head without pushing or modifying remote state.
4. Run the bundled helper to collect commit order plus review threads and replies:

```bash
SKILL_DIR="${SKILL_DIR:-<path-to-skill>}"
if [ -z "$SKILL_DIR" ]; then
  echo "Set SKILL_DIR to the installed review-stack skill directory" >&2
  exit 1
fi

OWNER="$(gh repo view --json owner --jq '.owner.login')"
REPO="$(gh repo view --json name --jq '.name')"
PR="<PR_NUMBER>"
BASE_REF="$(gh pr view "$PR" --repo "$OWNER/$REPO" --json baseRefName --jq '.baseRefName')"

mkdir -p _ai_report
CONTEXT_JSON="_ai_report/pr-${PR}-stack-context-$(date +%Y%m%d).json"
"$SKILL_DIR/scripts/get-stack-review-context" -o "$OWNER" -r "$REPO" -p "$PR" -u > "$CONTEXT_JSON"
```

5. Fetch code for local review:

```bash
git fetch origin "$BASE_REF"
git fetch origin "pull/${PR}/head:refs/remotes/origin/pr-${PR}"
BASE="$(git merge-base "origin/$BASE_REF" "refs/remotes/origin/pr-${PR}")"
```

6. For each commit in PR order, inspect it independently:

```bash
git show --stat --find-renames <COMMIT_SHA>
git show --format=fuller --find-renames <COMMIT_SHA> --
```

7. For each commit, write `_ai_report/pr-NUM-COMMITID.md`, where `COMMITID` is the short commit id from the PR stack. Use `assets/commit-review-template.md`.
8. Include the changed lines or relevant diff hunks for every finding, plus any related existing review thread.
9. Include replies to existing comments as context under the same thread. Do not repeat replies as separate comments or findings unless the reply introduces a distinct unresolved issue.
10. Label every finding with exactly one severity: `blocker`, `major`, `minor`, or `nit`.
11. If a commit has no findings, still write its report with `Result: no findings`.

## Review Rules

- Review the current commit's diff against its first parent, not the aggregate PR diff.
- Preserve atomicity in the review: do not blame a commit for behavior introduced only by a later commit.
- Call out atomicity problems when the commit depends on a later commit to build, test, or make semantic sense.
- Treat existing review comments as context, not as automatic findings.
- Use replies to understand whether a thread was answered, resolved, rejected, or still needs attention.
- Prefer precise line-level findings over broad commentary.
- Do not post GitHub comments, approve, request changes, push, or modify code unless the user explicitly asks.

## Report Contents

Each `_ai_report/pr-NUM-COMMITID.md` report must include:

- PR number, repository, commit id, commit subject, and generated date
- commit scope summary
- existing review threads for that commit, deduplicated by thread, with replies nested
- findings table with severity or `nit`
- detailed findings with path, line or hunk, rationale, and suggested fix when useful
- atomicity notes
- result status: `findings`, `nit-only`, or `no findings`

Severity guide:

- `blocker`: correctness, data loss, security, build failure, or a regression that should block merge
- `major`: important behavior, maintainability, or test coverage problem that should be fixed before merge
- `minor`: localized issue with limited risk
- `nit`: style, naming, wording, or very small cleanup that should not block merge

## Final Response

Summarize the PR number, commits reviewed, report paths written, counts by severity including nits, and any commits that could not be reviewed. Keep the final concise and state that no GitHub comments were posted.
